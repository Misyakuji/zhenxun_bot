import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter

from ....base_model import Result
from ....utils import authentication, get_system_disk
from .model import AddFile, DeleteFile, DirFile, RenameFile

router = APIRouter(prefix="/system")



@router.get("/get_dir_list", dependencies=[authentication()], description="获取文件列表")
async def _(path: Optional[str] = None) -> Result:
  base_path = Path(path) if path else Path()
  data_list = []
  for file in os.listdir(base_path):
    data_list.append(DirFile(is_file=not (base_path / file).is_dir(), name=file, parent=path))
  return Result.ok(data_list)


@router.get("/get_resources_size", dependencies=[authentication()], description="获取文件列表")
async def _(full_path: Optional[str] = None) -> Result:
  return Result.ok(await get_system_disk(full_path))


@router.post("/delete_file", dependencies=[authentication()], description="删除文件")
async def _(param: DeleteFile) -> Result:
  path = Path(param.full_path)
  if not path or not path.exists():
    return Result.warning_("文件不存在...")
  try:
    path.unlink()
    return Result.ok('删除成功!')
  except Exception as e:
    return Result.warning_('删除失败: ' + str(e))
  
@router.post("/delete_folder", dependencies=[authentication()], description="删除文件夹")
async def _(param: DeleteFile) -> Result:
  path = Path(param.full_path)
  if not path or not path.exists() or path.is_file():
    return Result.warning_("文件夹不存在...")
  try:
    shutil.rmtree(path.absolute())
    return Result.ok('删除成功!')
  except Exception as e:
    return Result.warning_('删除失败: ' + str(e))
  

@router.post("/rename_file", dependencies=[authentication()], description="重命名文件")
async def _(param: RenameFile) -> Result:
  path = (Path(param.parent) / param.old_name) if param.parent else Path(param.old_name)
  if not path or not path.exists():
    return Result.warning_("文件不存在...")
  try:
    path.rename(path.parent / param.name)
    return Result.ok('重命名成功!')
  except Exception as e:
    return Result.warning_('重命名失败: ' + str(e))
  

@router.post("/rename_folder", dependencies=[authentication()], description="重命名文件夹")
async def _(param: RenameFile) -> Result:
  path = (Path(param.parent) / param.old_name) if param.parent else Path(param.old_name)
  if not path or not path.exists() or path.is_file():
    return Result.warning_("文件夹不存在...")
  try:
    new_path = path.parent / param.name
    shutil.move(path.absolute(), new_path.absolute())
    return Result.ok('重命名成功!')
  except Exception as e:
    return Result.warning_('重命名失败: ' + str(e))
  

@router.post("/add_file", dependencies=[authentication()], description="新建文件")
async def _(param: AddFile) -> Result:
  path = (Path(param.parent) / param.name) if param.parent else Path(param.name)
  if path.exists():
    return Result.warning_("文件已存在...")
  try:
    path.open('w')
    return Result.ok('新建文件成功!')
  except Exception as e:
    return Result.warning_('新建文件失败: ' + str(e))