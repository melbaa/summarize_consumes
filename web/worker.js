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
                    
                # Ищем имена игроков
                if any(x in line for x in ['SPELL_', 'SWING_', 'ENCHANT_', 'RANGE_', 'DAMAGE_']):
                    parts = line.split(',')
                    if len(parts) > 2:
                        player_name = parts[1].strip().strip('"').strip()
                        if (player_name and len(player_name) > 1 and 
                            player_name != 'YOU' and 
                            player_name != 'Environment' and
                            not player_name.startswith('0x')):
                            players.add(player_name)
                
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
            
            # Создаём отчёт
            report = f"""🐢 Turtle WoW Consumables Analysis - Ambershire Server
Version: {self.version}

📊 LOG SUMMARY:
File size: {file_size}
Total lines: {total_lines}
Players detected: {len(sorted_players)}

👥 PLAYERS FOUND:
{', '.join(sorted_players[:25])}{'...' if len(sorted_players) > 25 else ''}

💊 CONSUMABLE USAGE:
{self.format_consumable_usage(consumable_usage)}

💰 PRICE DATA:
Items loaded: {len(self.price_db.prices) if prices_loaded else 0}
Price status: {'✓ Live prices loaded' if prices_loaded else '✗ Prices unavailable'}
Last update: {self.price_db.timestamp or 'Unknown'}

⚙️ TECHNICAL INFO:
This is the independent Ambershire-only version
Running on GitHub Pages - No external dependencies

📝 NOTES:
- Shows basic log analysis with consumable detection
- Using live Ambershire price data from our repository
- Full detailed analysis coming soon!"""
            
            print("✓ Analysis complete!")
            return report
            
        except Exception as e:
            import traceback
            error_msg = f"Analysis error: {str(e)}\\n{traceback.format_exc()}"
            print(error_msg)
            return error_msg

    def format_consumable_usage(self, usage_dict):
        """Форматируем использование потребляемых предметов"""
        if not usage_dict:
            return "   No consumables detected in log data"
        
        result = []
        for item, count in sorted(usage_dict.items(), key=lambda x: x[1], reverse=True):
            result.append(f"   {item}: {count} uses")
        return '\\n'.join(result)

# Создаём глобальный анализатор
analyzer = ConsumableAnalyzer()

def process_log_file(log_content):
    """Основная функция для обработки лога Амбершира"""
    result = analyzer.analyze_log(log_content)
    print(f"Process result type: {type(result)}, value: {result}")
    return result

print("✓ Ambershire analyzer ready!")
`;

    try {
        // Выполняем Python код
        await self.pyodide.runPythonAsync(pythonCode);
        
        // Тестируем загрузку
        const testResult = await self.pyodide.runPythonAsync(`
            try:
                test_result = f"✓ Ambershire analyzer loaded! Version: {analyzer.version}"
                print("Test result:", test_result)
                test_result
            except Exception as e:
                error_msg = f"✗ Error: {str(e)}"
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

        // Используем наш анализатор с правильным возвратом значения
        const analysisResult = await self.pyodide.runPythonAsync(`
            import json
            try:
                log_text = ${JSON.stringify(text)}
                result = process_log_file(log_text)
                print("Final result:", result)
                
                # Явно возвращаем результат
                if result is None:
                    result = "Error: Analysis returned None"
                
                # Убедимся что это строка
                str(result)
            except Exception as e:
                import traceback
                error_msg = f"Processing error: {str(e)}\\n{traceback.format_exc()}"
                print("Final error:", error_msg)
                error_msg
        `);
        
        console.log("Analysis result received:", analysisResult);
        
        self.postMessage({type:'doneprocessing'});
        
        // Убедимся что результат есть
        if (analysisResult && analysisResult !== "undefined" && analysisResult !== "None") {
            output_append('summaryoutput', analysisResult);
        } else {
            output_append('summaryoutput', "Error: No valid analysis result received. Check console for details.");
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
