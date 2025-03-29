import torch, platform

# 시스템 환경 검증
print(f"Python: {platform.python_version()}")
print(f"PyTorch: {torch.__version__}")
print(f"macOS: {platform.mac_ver()[0]}")  # 12.3+ 필요
print(f"MPS built: {torch.backends.mps.is_built()}")
print(f"MPS available: {torch.backends.mps.is_available()}")

if not (torch.backends.mps.is_available() and torch.backends.mps.is_built()):
    print("MPS 기능이 활성화 되지 않는 걸 보니, 구태여 모듈을 포함할 필요가 없어 보입니다.")
    exit(1)

# MPS 기능 활성화
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# 텐서 생성 및 이동
x = torch.rand(5, 5).to(device)  # 직접 device 지정
y = torch.ones(3, 3, device=device)  # 생성 시 할당
print(x.device, y.device)  # 출력: mps:0 mps:0
torch.mps.empty_cache()  # VRAM 정리

# 필수 조건 검증
assert torch.backends.mps.is_available(), "MPS 미활성"
assert torch.backends.mps.is_built(), "MPS 빌드 누락"
