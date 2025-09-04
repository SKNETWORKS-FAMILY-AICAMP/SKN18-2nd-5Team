import os
import random
import numpy as np

# try...except 블록을 포함한 torch 관련 코드를 제거합니다.
# 현재 모델링 작업에는 torch가 필요하지 않습니다.

DEFAULT_PATH = './archive/hotel_bookings.csv'
RANDOM_STATE = 42


def reset_seeds(seed: int = RANDOM_STATE) -> None:
    """Reset random seeds for reproducibility across numpy, random, and torch.

    If torch is not available, silently skip torch seeding.
    """
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    # torch 관련 코드를 제거하여 불필요한 로딩을 막습니다.
    # if torch is not None:
    #     torch.manual_seed(seed)
    #     if hasattr(torch, 'cuda'):
    #         try:
    #             torch.cuda.manual_seed(seed)
    #             torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
    #         except Exception:
    #             pass