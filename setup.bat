@echo off
chcp 65001 >nul
set HF_HOME=D:\40_Coursework\hf_cache
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

echo ========================================
echo VLA project environment
echo ========================================
echo HF_HOME = %HF_HOME%
python --version 2>nul
python -c "import torch; print('torch =', torch.__version__); print('cuda =', torch.cuda.is_available())" 2>nul
echo.
echo Offline interface test:
echo   python models\test_vla_interface.py
echo.
echo Real OpenVLA/LIBERO rollout requires a compatible Linux CUDA environment.
echo ========================================

cmd /k
