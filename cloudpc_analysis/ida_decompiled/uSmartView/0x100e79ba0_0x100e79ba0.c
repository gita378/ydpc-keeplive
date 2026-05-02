// 0x100e79ba0 @ 0x100e79ba0
__int64 __fastcall ikcp_send_link_sync(__int64 a1, unsigned __int8 a2, unsigned __int8 a3, char a4, unsigned __int8 a5)
{
  char v5; // r10
  char v6; // al
  char v7; // r10
  char v8; // r10
  char v9; // bl
  int v10; // ebx
  __int64 v11; // rsi
  const char *v12; // rdi
  __int64 v13; // rdx
  __int64 v14; // r8
  __int64 v15; // r9
  __int64 v16; // rcx
  __int64 v17; // rcx
  __int64 v18; // rdx
  __int64 v19; // r8
  __int64 v20; // r9
  char *v22; // [rsp+58h] [rbp-108h]
  _DWORD __b[24]; // [rsp+60h] [rbp-100h] BYREF
  unsigned int v24; // [rsp+C0h] [rbp-A0h]
  unsigned __int8 v25; // [rsp+C4h] [rbp-9Ch]
  char v26; // [rsp+C5h] [rbp-9Bh]
  unsigned __int8 v27; // [rsp+C6h] [rbp-9Ah]
  unsigned __int8 v28; // [rsp+C7h] [rbp-99h]
  __int64 v29; // [rsp+C8h] [rbp-98h]
  _BYTE v30[112]; // [rsp+D0h] [rbp-90h] BYREF

  v29 = a1; /*0x100e79bc0*/
  v28 = a2; /*0x100e79bc7*/
  v27 = a3; /*0x100e79bce*/
  v26 = a4; /*0x100e79bd4*/
  v25 = a5; /*0x100e79bda*/
  memset(__b, 0, sizeof(__b)); /*0x100e79bf5*/
  __b[4] = -2147483647; /*0x100e79bfa*/
  __b[7] = *(_DWORD *)(a1 + 12416); /*0x100e79c11*/
  v5 = 0; /*0x100e79c2d*/
  if ( v27 ) /*0x100e79c34*/
    v5 = 2; /*0x100e79c34*/
  v6 = v5 | a2; /*0x100e79c38*/
  v7 = 0; /*0x100e79c51*/
  if ( *(_BYTE *)(v29 + 12406) ) /*0x100e79c42*/
    v7 = 4; /*0x100e79c58*/
  LOBYTE(__b[5]) = v7 | v6; /*0x100e79c5f*/
  v8 = 0; /*0x100e79c74*/
  if ( v26 ) /*0x100e79c7b*/
    v8 = 16; /*0x100e79c7b*/
  LOBYTE(__b[5]) |= v8; /*0x100e79c89*/
  LOBYTE(__b[5]) |= 0x40u; /*0x100e79c9c*/
  v9 = 0; /*0x100e79cb5*/
  if ( v25 ) /*0x100e79cbb*/
    v9 = 0x80; /*0x100e79cbb*/
  LOBYTE(__b[5]) |= v9; /*0x100e79cca*/
  v10 = *(_DWORD *)(v29 + 96); /*0x100e79cd8*/
  *(_DWORD *)(v29 + 12420) = v10; /*0x100e79ce2*/
  __b[6] = v10; /*0x100e79ce8*/
  LOWORD(__b[9]) = *(_WORD *)(v29 + 24); /*0x100e79cfa*/
  __b[8] = *(_DWORD *)(v29 + 16); /*0x100e79d0c*/
  if ( *(_BYTE *)(v29 + 21109) == 1 ) /*0x100e79d29*/
  {
    HIWORD(__b[5]) = 0; /*0x100e79d2f*/
  }
  else if ( *(_BYTE *)(v29 + 21109) == 2 ) /*0x100e79d52*/
  {
    HIWORD(__b[5]) = 1; /*0x100e79d58*/
  }
  if ( *(_BYTE *)(v29 + 25232) == 1 ) /*0x100e79d7b*/
    HIWORD(__b[5]) |= 2u; /*0x100e79d8b*/
  if ( *(_BYTE *)(v29 + 27244) == 1 ) /*0x100e79da7*/
    HIWORD(__b[5]) |= 8u; /*0x100e79db7*/
  if ( *(_BYTE *)(v29 + 27246) == 1 ) /*0x100e79dd3*/
    HIWORD(__b[5]) |= 0x10u; /*0x100e79de3*/
  v11 = (__int64)v30; /*0x100e79dea*/
  *(_BYTE *)(v29 + 12407) = v28; /*0x100e79dfe*/
  *(_BYTE *)(v29 + 12452) = v27; /*0x100e79e11*/
  *(_BYTE *)(v29 + 12408) = 1; /*0x100e79e1e*/
  *(_BYTE *)(v29 + 18469) = v26; /*0x100e79e32*/
  *(_BYTE *)(v29 + 18470) = v25; /*0x100e79e45*/
  v12 = (const char *)v29; /*0x100e79e4b*/
  sub_100E74C10(v29, v30, __b); /*0x100e79e59*/
  *(_WORD *)(v29 + 20996) = 10; /*0x100e79e65*/
  *(_WORD *)(v29 + 20998) = 5; /*0x100e79e75*/
  v24 = 21; /*0x100e79e7e*/
  v16 = v29; /*0x100e79e88*/
  if ( *(_BYTE *)(v29 + 12411) ) /*0x100e79e8f*/
  {
    v22 = &v30[v24]; /*0x100e79eaf*/
    v12 = v22; /*0x100e79ebd*/
    ZXMemset(v22, 64, 0, 64); /*0x100e79ecb*/
    v24 += 64; /*0x100e79ede*/
    v17 = *(unsigned int *)(v29 + 20); /*0x100e79eeb*/
    v11 = (__int64)v22; /*0x100e79eee*/
    *(_DWORD *)v22 = v17; /*0x100e79ef5*/
    if ( (unsigned int)spice_util_get_debug(v22, v22, v18, v17, v19, v20) ) /*0x100e79ef7*/
    {
      if ( spice_gtk_log_level < 1 ) /*0x100e79f0f*/
      {
        v12 = "GSpice"; /*0x100e79f20*/
        v11 = 128; /*0x100e79f27*/
        g_log( /*0x100e79f42*/
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] kcp->last_conv:0x%x",
          (unsigned int)"ikcp_send_link_sync",
          3971,
          *(_DWORD *)(v29 + 20));
      }
    }
  }
  if ( (unsigned int)spice_util_get_debug(v12, v11, v13, v16, v14, v15) && spice_gtk_log_level < 1 ) /*0x100e79f6e*/
    g_log( /*0x100e7a04a*/
      (unsigned int)"GSpice",
      128,
      (unsigned int)"[%-38s:%4d] kcp:client udt support mode kcp->conv:0x%x be_ssl:%d, detech_mtu:%d be_multi:%d bu_quic:"
                    "%u be_algo_mode[%d] seg.wnd:%u",
      (unsigned int)"ikcp_send_link_sync",
      3980,
      *(_DWORD *)(v29 + 16),
      v28,
      v27,
      v25,
      *(unsigned __int8 *)(v29 + 27244),
      *(unsigned __int8 *)(v29 + 21109),
      HIWORD(__b[5]));
  return (unsigned int)sub_100E74F00(v29, v30, v24); /*0x100e7a090*/
}
