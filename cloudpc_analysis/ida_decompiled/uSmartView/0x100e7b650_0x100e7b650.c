// 0x100e7b650 @ 0x100e7b650
__int64 __fastcall ikcp_deal_reconnect(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  int v6; // r8d
  int v7; // r9d
  int v9; // [rsp+0h] [rbp-40h]

  if ( !*(_BYTE *)(a1 + 12411) ) /*0x100e7b664*/
  {
    if ( (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) && spice_gtk_log_level < 2 ) /*0x100e7b69a*/
    {
      v9 = *(unsigned __int8 *)(a1 + 12411); /*0x100e7b6dd*/
      g_log( /*0x100e7b6e3*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp reconnect, conv:0x%x, be_reconnect:%d",
        (unsigned int)"ikcp_deal_reconnect",
        3899,
        *(_DWORD *)(a1 + 16),
        v9);
    }
    ikcp_info( /*0x100e7b70c*/
      a1,
      (unsigned int)"kcp reconnect, conv:0x%x, be_reconnect:%d",
      *(_DWORD *)(a1 + 16),
      *(unsigned __int8 *)(a1 + 12411),
      v6,
      v7);
    *(_BYTE *)(a1 + 18456) = 0; /*0x100e7b715*/
    *(_BYTE *)(a1 + 12409) = 0; /*0x100e7b720*/
    *(_BYTE *)(a1 + 18472) = 0; /*0x100e7b72b*/
    *(_BYTE *)(a1 + 18476) = 0; /*0x100e7b736*/
    *(_BYTE *)(a1 + 12411) = 1; /*0x100e7b741*/
    *(_DWORD *)(a1 + 20) = *(_DWORD *)(a1 + 16); /*0x100e7b753*/
    *(_DWORD *)(a1 + 16) = 0; /*0x100e7b75a*/
    *(_BYTE *)(a1 + 18457) = 0; /*0x100e7b765*/
    if ( *(_BYTE *)(a1 + 18455) ) /*0x100e7b770*/
      ikcp_set_auth_data( /*0x100e7b7f9*/
        a1,
        a1 + 12455,
        *(_WORD *)(a1 + 18458),
        *(_WORD *)(a1 + 18460),
        *(_DWORD *)(a1 + 18464),
        *(_BYTE *)(a1 + 12407),
        *(_BYTE *)(a1 + 12452),
        *(_BYTE *)(a1 + 18469));
    else
      ikcp_update(a1, (unsigned int)a2); /*0x100e7b811*/
  }
  return 0; /*0x100e7b820*/
}
