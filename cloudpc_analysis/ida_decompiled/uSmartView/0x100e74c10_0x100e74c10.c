// 0x100e74c10 @ 0x100e74c10
_WORD *__fastcall sub_100E74C10(_BYTE *a1, __int64 a2, __int64 a3)
{
  _WORD *v4; // [rsp+8h] [rbp-A0h]

  *(_DWORD *)a2 = *(_DWORD *)(a3 + 16); /*0x100e74c5b*/
  *(_BYTE *)(a2 + 4) = *(_BYTE *)(a3 + 20); /*0x100e74cb0*/
  *(_WORD *)(a2 + 5) = *(_WORD *)(a3 + 22); /*0x100e74ce3*/
  *(_DWORD *)(a2 + 7) = *(_DWORD *)(a3 + 24); /*0x100e74d22*/
  *(_DWORD *)(a2 + 11) = *(_DWORD *)(a3 + 28); /*0x100e74d60*/
  *(_DWORD *)(a2 + 15) = *(_DWORD *)(a3 + 32); /*0x100e74d9e*/
  *(_WORD *)(a2 + 19) = *(_WORD *)(a3 + 36); /*0x100e74ddf*/
  v4 = (_WORD *)(a2 + 21); /*0x100e74df5*/
  if ( a1 && *(unsigned __int8 *)(a3 + 20) != 130 && a1[18469] && !a1[18456] ) /*0x100e74e40*/
  {
    *v4 = *(_WORD *)(a3 + 38); /*0x100e74e6f*/
    v4 = (_WORD *)(a2 + 23); /*0x100e74e84*/
  }
  if ( a1 && a1[25232] ) /*0x100e74ea0*/
  {
    *(_BYTE *)v4 = *(_BYTE *)(a3 + 56); /*0x100e74edd*/
    return (_WORD *)((char *)v4 + 1); /*0x100e74ee3*/
  }
  return v4; /*0x100e74ef1*/
}
