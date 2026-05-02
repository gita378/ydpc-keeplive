// 0x100e7b150 @ 0x100e7b150
__int64 __fastcall ikcp_get_seg_info(__int64 a1, __int64 a2)
{
  *(_DWORD *)(a2 + 16) = *(_DWORD *)a1; /*0x100e7b17d*/
  *(_BYTE *)(a2 + 20) = *(_BYTE *)(a1 + 4); /*0x100e7b1c5*/
  *(_WORD *)(a2 + 22) = *(_WORD *)(a1 + 5); /*0x100e7b1f3*/
  *(_DWORD *)(a2 + 24) = *(_DWORD *)(a1 + 7); /*0x100e7b22e*/
  *(_DWORD *)(a2 + 28) = *(_DWORD *)(a1 + 11); /*0x100e7b267*/
  *(_DWORD *)(a2 + 32) = *(_DWORD *)(a1 + 15); /*0x100e7b2a0*/
  *(_WORD *)(a2 + 36) = *(_WORD *)(a1 + 19); /*0x100e7b2db*/
  return a1 + 21; /*0x100e7b2f9*/
}
