"""Rotas de configurações do quadro. Camada fina (ADR-030)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.application.settings.board_settings_use_cases import (
    GetBoardSettingsUseCase,
    UpdateBoardSettingsUseCase,
)
from src.presentation.dependencies import (
    get_get_board_settings_use_case,
    get_update_board_settings_use_case,
)

router = APIRouter(prefix="/settings", tags=["settings"])


class BoardSettings(BaseModel):
    agents_can_create_tasks: bool


@router.get("/board", response_model=BoardSettings)
async def get_board_settings(
    use_case: GetBoardSettingsUseCase = Depends(get_get_board_settings_use_case),
) -> BoardSettings:
    return BoardSettings(agents_can_create_tasks=await use_case.agents_can_create_tasks())


@router.put("/board", response_model=BoardSettings)
async def put_board_settings(
    body: BoardSettings,
    use_case: UpdateBoardSettingsUseCase = Depends(get_update_board_settings_use_case),
) -> BoardSettings:
    await use_case.set_agents_can_create_tasks(body.agents_can_create_tasks)
    return body
