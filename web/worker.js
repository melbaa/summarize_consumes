importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js")

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage(["micropip"]);
    try {
        status_append("runtime loaded. installing libraries ...");

        // Устанавливаем зависимости
        await self.pyodide.runPythonAsync(`
            import micropip
            await micropip.install(['requests', 'humanize', 'plotly', 'tenacity'])
        `);

        // Загружаем ВЕСЬ код одним файлом
        await loadCombinedPythonCode();
        
        status_append("✓ All packages and code loaded successfully!");
    } catch (err) {
        self.postMessage({type:'loadliberror', data: err.message});
        console.error("Load error:", err);
        throw err;
    }
}

async function loadCombinedPythonCode() {
    // Создаём единый Python файл со ВСЕМ кодом
    const combinedCode = `
# === COMBINED SUMMARIZE_CONSUMES CODE ===

# Импорты
import json
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any

# Здесь будет ВЕСЬ код из всех файлов...
# Пока добавляем базовый импорт для теста

class ConsumableAnalyzer:
    def __init__(self):
        self.version = "2025.1121"
    
    def test(self):
        return f"Consumable Analyzer {self.version} - Ready!"

analyzer = ConsumableAnalyzer()

# Основная функция для тестирования
def process_test():
    return analyzer.test()

print("✓ Python code loaded successfully!")
`;

    // Выполняем объединённый код
    await self.pyodide.runPythonAsync(combinedCode);
    
    // Тестируем что код работает
    const testResult = await self.pyodide.runPythonAsync(`
        try:
            result = process_test()
            print("Test result:", result)
            result
        except Exception as e:
            f"Error in test: {str(e)}"
    `);
    
    console.log("Python test result:", testResult);
}

let pyodideReadyPromise = loadPyodideAndPackages();
status_append('worker started');

self.onmessage = async (event) => {
    await pyodideReadyPromise;

    try {
        const {server, file} = event.data;
        const text = await file.text();

        status_append(`processing ${file.name}. please wait ...`);
        
        // Пока используем демо-режим, пока не загрузили полный код
        const demoResult = await self.pyodide.runPythonAsync(`
            try:
                result = f"Demo mode: Processing log for {${JSON.stringify(server)}} server\\\\n"
                result += f"File: {${JSON.stringify(file.name)}}\\\\n" 
                result += f"Size: {len(${JSON.stringify(text)})} characters\\\\n"
                result += "Full analysis coming soon..."
                result
            except Exception as e:
                f"Demo error: {str(e)}"
        `);
        
        self.postMessage({type:'doneprocessing'});
        output_append('summaryoutput', demoResult);
        inputelem_show();
        
    } catch (error) {
        status_append(`Processing error: ${error}`);
        inputelem_show();
    }
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
