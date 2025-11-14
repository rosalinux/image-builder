# Сборка образа для OK3568C Rockchip устройства от RADXA

## Требования

- **Операционная система**: rosa13 fresh
- **Зависимости**: Убедитесь, что следующие пакеты установлены в системе:
  - `binutils-aarch64-linux-gnu`
  - `gcc-aarch64-linux-gnu`
  - `mkosi`
  - `qemu-aarch64-static`
  - `qemu-loongarch64-static`
  - `qemu-riscv64-static`
  - `uboot-tools`
  - `ok3568c-bootloader`

## Установка

2. **Установка зависимостей**:
   ```bash
   sudo dnf update
   sudo dnf in rosa-repos-contrib
   sudo dnf install mkosi qemu-aarch64-static uboot-tools gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu ok3568c-bootloader
   ```

## Использование

2. **Создание образа**:
   Запустите процесс сборки с указанием вашего конфигурационного файла:
   ```bash
   cd image-builder/rockchip/ok3568c
   mkosi --force
   ```
   По завершении сборки, готовый образ будет доступен в текущей директории.

## Поддержка

Если у вас возникли вопросы или проблемы, пожалуйста, создайте [issue](https://github.com/rosalinux/image-builder/issues) в этом репозитории.

## Лицензия

Этот проект распространяется под лицензией MIT.
