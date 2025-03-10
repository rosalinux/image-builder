# Boot Loader for Repka Pi 4

## Сборка загрузчика

### 1. Клонирование репозитория
Склонируйте репозиторий загрузчика с помощью команды:

```bash
git clone https://gitflic.ru/project/npo_rbs/repka-os_boot-loader.git
```

### 2. Загрузка подмодулей
Перейдите в директорию проекта и скачайте все подмодули:

```bash
cd repka-os_boot-loader
git submodule update --init --recursive
```

### 3. Сборка загрузчика
Запустите сборку командой:

```bash
make build-loader
```

### 4. Результат сборки
После успешной сборки появится директория `src` в корне репозитория, содержащая следующие файлы и папки:

```
src/
├── overlays/             # Директория с оверлеями для Repka Pi 4
│   ├── i2c1.dtbo
│   ├── i2c2.dtbo
│   ├── i2c3.dtbo
│   ├── i2s.dtbo
│   ├── i2s_pcm5102.dtbo
│   ├── i2s_pcm5122.dtbo
│   ├── spi0.dtbo
│   ├── s_uart.dtbo
│   ├── uart3.dtbo
│   └── w1_gpio.dtbo
├── repka-pi.dtb          # Основное дерево устройств для Repka Pi 4
└── spl/
    ├── u-boot-sunxi-with-spl.bin         # Загрузчик с логированием в UART0
    └── u-boot-sunxi-with-spl-silent.bin  # Загрузчик в тихом режиме
```

### 5. Копирование загрузчика
Скопируйте обе вариации загрузчика в `mkosi.extra/boot/spl/`:

```bash
cp -fv src/spl/*.bin mkosi.extra/boot/spl/
```

### Дополнительная информация
Если возникли вопросы или проблемы, обратитесь к документации проекта или откройте issue в репозитории.

