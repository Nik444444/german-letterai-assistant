#!/bin/bash

# Проверка и установка emergentintegrations
echo "Checking if emergentintegrations is available..."

# Пытаемся импортировать emergentintegrations
python -c "from emergentintegrations.llm.chat import LlmChat; print('✓ emergentintegrations already available')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "emergentintegrations not found, installing..."
    
    # Устанавливаем emergentintegrations
    pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ --trusted-host d33sy5i8bnduwe.cloudfront.net
    
    # Проверяем успешность установки
    python -c "from emergentintegrations.llm.chat import LlmChat; print('✓ emergentintegrations installed successfully')"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install emergentintegrations"
        exit 1
    fi
else
    echo "✓ emergentintegrations is already available"
fi

echo "✓ All checks passed, starting server..."
python server.py