# Boot Loader for Repka Pi 4

## Сборка загрузчика
Для сборки прошивки необходимо выполнить следующие команды:

# Клонировать репоpиторий загрузчика
    ```bash
    git clone https://gitflic.ru/project/npo_rbs/repka-os_boot-loader.git
    ```
 
# Скачать все подмодули с помощью команды:
    ```bash
    cd repka-os_boot-loader
    git submodule update --init --recursive
    ```

# Запустить сборку с помощью команды:
    ```bash
    make build-loader
    ```

# После успешной сборки появиться директория src в корне репозитория:
    ```
      src
       ├── overlays (директория с оверлеями для Repka Pi 4)
       │ ├── i2c1.dtbo
       │ ├── i2c2.dtbo
       │ ├── i2c3.dtbo
       │ ├── i2s.dtbo
       │ ├── i2s_pcm5102.dtbo
       │ ├── i2s_pcm5122.dtbo
       │ ├── spi0.dtbo
       │ ├── s_uart.dtbo
       │ ├── uart3.dtbo
       │ └── w1_gpio.dtbo
       ├── repka-pi.dtb (основное дерево устройств для Repka Pi 4)
       └── spl
       ├── u-boot-sunxi-with-spl.bin (загрузчик с включенным логированием в UART0)
       └── u-boot-sunxi-with-spl-silent.bin (загрузчик с тихим режимом)
    ```
# Скопировать обе вариации загрузчика в mkosi.extra/boot/spl/
    ```bash
    cp -fv src/spl/*.bin mkosi.extra/boot/spl/
    ```
