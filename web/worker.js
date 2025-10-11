importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js")

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage(["micropip"]);
    try {
        status_append("runtime loaded. installing libraries ...");

        // Устанавливаем только необходимые зависимости
        await self.pyodide.runPythonAsync(`
            import micropip
            await micropip.install(['requests', 'humanize'])
        `);

        // Загружаем наш Python код
        await loadCompletePythonCode();
        
        status_append("✓ All packages and code loaded successfully!");
    } catch (err) {
        self.postMessage({type:'loadliberror', data: "Failed to load libraries: " + err.message});
        console.error("Load error:", err);
        throw err;
    }
}

async function loadCompletePythonCode() {
    const pythonCode = `
# === TURTLE WOW CONSUMABLES ANALYZER - AMBERSHIRE VERSION ===
import json
import re
import time
from datetime import datetime
import requests
from humanize import naturalsize

print("✓ Starting Turtle WoW Ambershire Consumables Analyzer...")

# Константы
VERSION = "2025.1121.ambershire"

# ТОЛЬКО наш URL для цен Амбершира
AMBERSHIRE_PRICE_URL = "https://raw.githubusercontent.com/whtmst/twow-ambershire-prices/main/ambershire-prices-full.json"

class PriceDatabase:
    def __init__(self):
        self.prices = {}
        self.timestamp = None
        
    def load_ambershire_prices(self):
        """Загружаем цены для Амбершира"""
        try:
            print("Loading Ambershire prices...")
            response = requests.get(AMBERSHIRE_PRICE_URL, timeout=10)
            if response.status_code == 200:
                self.prices = response.json()
                self.timestamp = datetime.now().isoformat()
                print(f"✓ Loaded Ambershire prices: {len(self.prices)} items")
                return True
            else:
                print(f"✗ Failed to load prices: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Error loading prices: {e}")
        return False

class ConsumableAnalyzer:
    def __init__(self):
        self.price_db = PriceDatabase()
        self.version = VERSION
        
    def analyze_log(self, log_content):
        """Анализируем лог для Амбершира"""
        try:
            print("Starting log analysis...")
            
            # Загружаем цены Амбершира
            print("Loading price data...")
            prices_loaded = self.price_db.load_ambershire_prices()
            
            # Базовый анализ лога
            lines = log_content.split('\\n')
            total_lines = len(lines)
            file_size = naturalsize(len(log_content))
            
            print(f"Analyzing {total_lines} lines ({file_size})...")
            
            # Ищем имена игроков в логе
            players = set()
            consumable_usage = {}
            
            # Простые паттерны для потребляемых предметов
            for i, line in enumerate(lines):
                if i > 50000:  # Ограничим для скорости
                    break
                    
                # Ищем имена игроков - улучшенный парсинг
                if any(x in line for x in ['SPELL_', 'SWING_', 'ENCHANT_', 'RANGE_', 'DAMAGE_', 'PARTY_']):
                    # Пробуем разные способы парсинга
                    parts = line.split(',')
                    if len(parts) > 2:
                        # Пробуем разные позиции для имени игрока
                        for pos in [1, 2, 3]:
                            if pos < len(parts):
                                player_name = parts[pos].strip().strip('"').strip("'").strip()
                                if (player_name and 
                                    len(player_name) > 1 and 
                                    len(player_name) < 20 and
                                    player_name != 'YOU' and 
                                    player_name != 'Environment' and
                                    not player_name.startswith('0x') and
                                    not player_name.isdigit() and
                                    ' ' not in player_name):
                                    players.add(player_name)
                                    break
                
                # Ищем использование зелий
                line_lower = line.lower()
                if any(x in line_lower for x in ['potion', 'elixir', 'flask', 'scroll', 'food']):
                    if 'major mana potion' in line_lower:
                        consumable_usage['Major Mana Potion'] = consumable_usage.get('Major Mana Potion', 0) + 1
                    elif 'major healing potion' in line_lower:
                        consumable_usage['Major Healing Potion'] = consumable_usage.get('Major Healing Potion', 0) + 1
                    elif 'elixir of the mongoose' in line_lower:
                        consumable_usage['Elixir of the Mongoose'] = consumable_usage.get('Elixir of the Mongoose', 0) + 1
                    elif 'flask of' in line_lower:
                        consumable_usage['Flask'] = consumable_usage.get('Flask', 0) + 1
                    elif 'elixir' in line_lower:
                        consumable_usage['Other Elixirs'] = consumable_usage.get('Other Elixirs', 0) + 1
                    elif 'scroll' in line_lower:
                        consumable_usage['Scrolls'] = consumable_usage.get('Scrolls', 0) + 1
            
            # Сортируем игроков по алфавиту
            sorted_players = sorted(players)
            
            # Создаём отчёт БЕЗ эмодзи для совместимости
            report_lines = []
            report_lines.append("Turtle WoW Consumables Analysis - Ambershire Server")
            report_lines.append(f"Version: {self.version}")
            report_lines.append("")
            report_lines.append("LOG SUMMARY:")
            report_lines.append(f"File size: {file_size}")
            report_lines.append(f"Total lines: {total_lines}")
            report_lines.append(f"Players detected: {len(sorted_players)}")
            report_lines.append("")
            report_lines.append("PLAYERS FOUND:")
            if sorted_players:
                # Показываем только первых 25 игроков
                players_display = ', '.join(sorted_players[:25])
                if len(sorted_players) > 25:
                    players_display += '...'
                report_lines.append(players_display)
            else:
                report_lines.append("No players detected - check log format")
            report_lines.append("")
            report_lines.append("CONSUMABLE USAGE:")
            report_lines.append(self.format_consumable_usage(consumable_usage))
            report_lines.append("")
            report_lines.append("PRICE DATA:")
            report_lines.append(f"Items loaded: {len(self.price_db.prices) if prices_loaded else 0}")
            report_lines.append(f"Price status: {'Live prices loaded' if prices_loaded else 'Prices unavailable'}")
            report_lines.append(f"Last update: {self.price_db.timestamp or 'Unknown'}")
            report_lines.append("")
            report_lines.append("TECHNICAL INFO:")
            report_lines.append("This is the independent Ambershire-only version")
            report_lines.append("Running on GitHub Pages - No external dependencies")
            report_lines.append("")
            report_lines.append("NOTES:")
            report_lines.append("- Shows basic log analysis with consumable detection")
            report_lines.append("- Using live Ambershire price data from our repository")
            report_lines.append("- Full detailed analysis coming soon!")
            
            report = '\\\\n'.join(report_lines)
            print("✓ Analysis complete! Report length:", len(report))
            return report
            
        except Exception as e:
            import traceback
            error_msg = f"Analysis error: {str(e)}\\\\n{traceback.format_exc()}"
            print(error_msg)
            return error_msg

    def format_consumable_usage(self, usage_dict):
        """Форматируем использование потребляемых предметов"""
        if not usage_dict:
            return "   No consumables detected in log data"
        
        result = []
        for item, count in sorted(usage_dict.items(), key=lambda x: x[1], reverse=True):
            result.append(f"   {item}: {count} uses")
        return '\\\\n'.join(result)

# Создаём глобальный анализатор
analyzer = ConsumableAnalyzer()

def process_log_file(log_content):
    """Основная функция для обработки лога Амбершира"""
    result = analyzer.analyze_log(log_content)
    print(f"Process result type: {type(result)}, length: {len(result) if result else 0}")
    
    # Записываем результат в файл чтобы избежать проблем с возвратом
    with open('/analysis_result.txt', 'w', encoding='utf-8') as f:
        f.write(result if result else "No result")
    
    return "SUCCESS"  # Возвращаем простой статус

print("✓ Ambershire analyzer ready!")
`;

    try {
        // Выполняем Python код
        await self.pyodide.runPythonAsync(pythonCode);
        
        // Тестируем загрузку
        const testResult = await self.pyodide.runPythonAsync(`
            try:
                test_result = "✓ Ambershire analyzer loaded! Version: " + analyzer.version
                print("Test:", test_result)
                test_result
            except Exception as e:
                error_msg = "✗ Error: " + str(e)
                print("Test error:", error_msg)
                error_msg
        `);
        
        console.log("Python initialization:", testResult);
        
    } catch (error) {
        throw new Error(`Failed to initialize Python: ${error}`);
    }
}

let pyodideReadyPromise = loadPyodideAndPackages();
status_append('worker started');

self.onmessage = async (event) => {
    await pyodideReadyPromise;

    try {
        const {server, file} = event.data;
        const text = await file.text();

        status_append(`processing ${file.name} for Ambershire server...`);
        console.log("Starting analysis for file:", file.name, "size:", text.length);

        // Запускаем анализ и записываем результат в файл
        const processStatus = await self.pyodide.runPythonAsync(`
            try:
                log_text = ${JSON.stringify(text)}
                status = process_log_file(log_text)
                print("Process status:", status)
                status
            except Exception as e:
                import traceback
                error_msg = "Processing error: " + str(e) + "\\\\n" + traceback.format_exc()
                print("Final error:", error_msg)
                # Записываем ошибку в файл
                with open('/analysis_result.txt', 'w', encoding='utf-8') as f:
                    f.write(error_msg)
                "ERROR"
        `);
        
        console.log("Process status:", processStatus);
        
        // Читаем результат из файла
        let analysisResult;
        try {
            analysisResult = self.pyodide.FS.readFile("/analysis_result.txt", { encoding: "utf8" });
            console.log("Analysis result from file:", analysisResult.length, "characters");
        } catch (fileError) {
            analysisResult = "Error reading result file: " + fileError.message;
            console.error("File read error:", fileError);
        }
        
        self.postMessage({type:'doneprocessing'});
        
        // Выводим результат
        if (analysisResult && analysisResult.length > 0) {
            output_append('summaryoutput', analysisResult);
        } else {
            output_append('summaryoutput', "Analysis completed but result is empty. Check browser console for details.");
        }
        
        inputelem_show();
        
    } catch (error) {
        const errorMsg = `Error: ${error.message}`;
        console.error("Worker error:", error);
        status_append(errorMsg);
        output_append('summaryoutput', errorMsg);
        inputelem_show();
    }
};

function status_append(txt) {
    output_append('statusoutput', txt)
}

function output_append(eleid, txt) {
    let msgtype = eleid + 'append'
    self.postMessage({type:msgtype, data: txt || "Empty result"});
}

function inputelem_show() {
    self.postMessage({type:'inputshow'});
}
