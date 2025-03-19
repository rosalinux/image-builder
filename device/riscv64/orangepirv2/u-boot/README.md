# U-Boot for Orange Pi RV2 (riscv64)

Этот репозиторий содержит инструкции по сборке U-Boot для Orange Pi RV2 на архитектуре RISC-V.

## Требования

Перед началом убедитесь, что у вас установлен необходимый компилятор и утилиты:

```sh
sudo dnf install gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu make
```
## Автоматическая сборка U-Boot
1. в каталоге u-boot выполнить
   ```sh
   make
   ```

## Ручная сборка U-Boot

1. Клонируйте репозиторий U-Boot:
   
   ```sh
   git clone https://github.com/orangepi-xunlong/u-boot-orangepi.git -b v2022.10-ky --depth 1
   ```

2. Перейдите в директорию с кодом:
   
   ```sh
   cd u-boot-orangepi
   ```

3. Настройте конфигурацию:
   
   ```sh
   make x1_defconfig
   ```

4. Соберите U-Boot:
   
   ```sh
   make -s -j24 CROSS_COMPILE=riscv64-linux-gnu-
   ```

## Дополнительная информация

- [Официальный сайт Orange Pi](http://www.orangepi.org/)
- [Репозиторий U-Boot](https://github.com/orangepi-xunlong/u-boot-orangepi)
