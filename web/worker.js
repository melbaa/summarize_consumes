importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js")

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage(["micropip"]);
    try {
        status_append("runtime loaded. installing libraries ...");

        // Устанавливаем зависимости
        await self.pyodide.runPythonAsync(`
            import micropip
            # Устанавливаем необходимые пакеты
            await micropip.install(['requests', 'humanize', 'plotly'])
        `);

        // Загружаем код напрямую из репозитория
        await loadPythonCode();
        
        status_append("✓ All packages and code loaded successfully!");
    } catch (err) {
        self.postMessage({type:'loadliberror', data:err.message});
        throw err;
    }
}

async function loadPythonCode() {
    const baseUrl = "https://raw.githubusercontent.com/whtmst/summarize_consumes/main/src/melbalabs/summarize_consumes/";
    
    // Загружаем все необходимые Python файлы
    const files = [
        '__init__.py',
        'consumable_db.py', 
        'consumable_model.py',
        'grammar.py',
        'main.py',
        'package.py',
        'parser.py'
    ];

    for (const file of files) {
        const response = await fetch(baseUrl + file);
        if (!response.ok) {
            throw new Error(`Failed to load ${file}: ${response.statusText}`);
        }
        const code = await response.text();
        
        // Выполняем код в Pyodide
        await self.pyodide.runPythonAsync(code);
    }
}

let pyodideReadyPromise = loadPyodideAndPackages();
status_append('worker started');

// Остальной код без изменений...
self.onmessage = async (event) => {
    await pyodideReadyPromise;

    const {server, file} = event.data;
    const text = await file.text();

    status_append(`processing ${file.name}. please wait ...`);

    pyodide.FS.writeFile('log.txt', text, {encoding: 'utf8'});

    await pyodide.runPythonAsync(`
        from melbalabs.summarize_consumes.main import main

        argv = ['log.txt', '--write-summary', '--prices-server', '${server}',
                '--write-damage-output', '--write-healing-output', '--write-damage-taken-output']
        main(argv)
    `);
    
    let summaryoutput = pyodide.FS.readFile("summary.txt", {encoding: 'utf8'});
    let damageoutput = pyodide.FS.readFile("damage-output.txt", {encoding: 'utf8'});
    let healingoutput = pyodide.FS.readFile("healing-output.txt", {encoding: 'utf8'});
    let damagetakenoutput = pyodide.FS.readFile('damage-taken-output.txt', {encoding: 'utf8'});
    
    self.postMessage({type:'doneprocessing'});
    output_append('summaryoutput', summaryoutput);
    output_append('damageoutput', damageoutput);
    output_append('healingoutput', healingoutput);
    output_append('damagetakenoutput', damagetakenoutput);
    inputelem_show();
};

function status_append(txt) {
    output_append('statusoutput', txt)
}

function output_append(eleid, txt) {
    let msgtype = eleid + 'append'
    self.postMessage({type:msgtype, data:txt});
}

function inputelem_show() {
    self.postMessage({type:'inputshow'});
}
