# TODO for `image-builder` Project

1. **Add a handler for `boot.cmd`**  
   - Implement processing and integration of `boot.cmd` during image creation.  
   - Ensure compatibility with common boot scenarios.

2. **Kernel Build from Custom Configurations**  
   - Develop a mechanism to compile the Linux kernel using custom `.config` files.  
   - Provide clear documentation for users to supply and use their own configurations.

3. **Custom Kernel Installation (Non-Repository)**  
   - Design a solution for installing custom-built kernels that are not available in standard repositories.  
   - Consider integrating a kernel packaging or direct installation process.

4. **Enhance U-Boot Writing Functionality**  
   - Finalize the function for writing U-Boot to `/dev/loopX`.  
   - Add error handling, validation, and logging to ensure robustness.

5. **Finalize Loop Device Unmount Function**  
   - Complete the function to properly unmount `/dev/loop` devices after use.  
   - Implement safeguards to prevent accidental unmounting of active devices.

6. **Root Password Setup**  
   - Resolve issues with `systemd-firstboot` for setting the root password.  
   - Implement a workaround to delete the default `root` user before initializing a new password.  
   - Alternatively, explore other methods for securely setting the root password during image creation.

