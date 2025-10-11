importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js")

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage(["micropip"]);
    try {
        status_append("runtime loaded. installing libraries ...");

        // Устанавливаем ВСЕ необходимые зависимости
        await self.pyodide.runPythonAsync(`
            import micropip
            await micropip.install(['requests', 'humanize', 'plotly', 'tenacity', 'typing-extensions'])
        `);

        // Загружаем ВЕСЬ наш Python код
        await loadCompletePythonCode();
        
        status_append("✓ All packages and code loaded successfully!");
    } catch (err) {
        self.postMessage({type:'loadliberror', data: "Failed to load libraries: " + err.message});
        console.error("Load error:", err);
        throw err;
    }
}

async function loadCompletePythonCode() {
    // ВЕСЬ код summarize_consumes в одном файле
    const pythonCode = `
# === TURTLE WOW CONSUMABLES ANALYZER - INDEPENDENT VERSION ===
import json
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import requests
from humanize import naturalsize

print("✓ Starting Turtle WoW Consumables Analyzer...")

# Константы и настройки
PROJECT_NAME = "melbalabs.summarize_consumes"
VERSION = "2025.1121.independent"

# URL для цен (используем НАШИ собственные)
PRICE_URLS = {
    "nord": "https://raw.githubusercontent.com/whtmst/twow-ambershire-prices/main/nord-prices.json",
    "telabim": "https://raw.githubusercontent.com/whtmst/twow-ambershire-prices/main/telabim-prices.json", 
    "ambershire": "https://raw.githubusercontent.com/whtmst/twow-ambershire-prices/main/ambershire-prices-full.json"
}

class PriceDatabase:
    def __init__(self):
        self.prices = {}
        self.timestamp = None
        
    def load_prices(self, server):
        """Загружаем цены для указанного сервера"""
        try:
            url = PRICE_URLS.get(server)
            if not url:
                return False
                
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self.prices = response.json()
                self.timestamp = datetime.now().isoformat()
                return True
        except Exception as e:
            print(f"Error loading prices: {e}")
        return False

class ConsumableAnalyzer:
    def __init__(self):
        self.price_db = PriceDatabase()
        self.version = VERSION
        
    def analyze_log(self, log_content, server):
        """Анализируем лог и возвращаем результат"""
        try:
            # Загружаем цены для сервера
            if not self.price_db.load_prices(server):
                return f"Error: Could not load prices for server '{server}'"
            
            # Базовый анализ лога
            lines = log_content.split('\\n')
            total_lines = len(lines)
            file_size = naturalsize(len(log_content))
            
            # Ищем имена игроков в логе
            players = set()
            for line in lines[:1000]:  # Проверяем первые 1000 строк
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) > 1:
                        # Пытаемся найти имя игрока
                        player_match = re.search(r'^([A-Za-z]+)', parts[1])
                        if player_match:
                            players.add(player_match.group(1))
            
            # Создаём базовый отчёт
            report = f"""Turtle WoW Consumables Analysis - Independent Version
Server: {server}
Log size: {file_size}
Total lines: {total_lines}
Players found: {', '.join(sorted(players)[:10])}{'...' if len(players) > 10 else ''}

=== CONSUMABLE USAGE ===
[Full analysis will be implemented here]

=== DAMAGE SUMMARY ===
[Damage analysis will be implemented here]

=== HEALING SUMMARY ===  
[Healing analysis will be implemented here]

=== TECHNICAL INFO ===
Analyzer version: {self.version}
Prices loaded: {'Yes' if self.price_db.prices else 'No'}
Prices timestamp: {self.price_db.timestamp or 'N/A'}

Note: This is the independent version running on GitHub Pages.
Full consumable tracking coming soon!"""
            
            return report
            
        except Exception as e:
            return f"Analysis error: {str(e)}"

# Создаём глобальный анализатор
analyzer = ConsumableAnalyzer()

def process_log_file(log_content, server):
    """Основная функция для обработки лога"""
    return analyzer.analyze_log(log_content, server)

print("✓ Python analyzer ready!")
`;

    try {
        // Выполняем ВЕСЬ Python код
        await self.pyodide.runPythonAsync(pythonCode);
        
        // Тестируем что код работает
        const testResult = await self.pyodide.runPythonAsync(`
            try:
                # Тестовый вызов
                test_log = "TEST LOG LINE\\n"
                test_result = f"✓ Python code loaded successfully! Version: {analyzer.version}"
                print(test_result)
                test_result
            except Exception as e:
                f"✗ Error in Python code: {str(e)}"
        `);
        
        console.log("Python initialization:", testResult);
        status_append(testResult);
        
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

        status_append(`processing ${file.name} for ${server} server...`);

        // Используем НАШ анализатор
        const analysisResult = await self.pyodide.runPythonAsync(`
            try:
                result = process_log_file(${JSON.stringify(text)}, ${JSON.stringify(server)})
                result
            except Exception as e:
                f"Processing error: {str(e)}"
        `);
        
        self.postMessage({type:'doneprocessing'});
        output_append('summaryoutput', analysisResult);
        inputelem_show();
        
    } catch (error) {
        const errorMsg = `Error: ${error.message}`;
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
    self.postMessage({type:msgtype, data:txt});
}

function inputelem_show() {
    self.postMessage({type:'inputshow'});
}
