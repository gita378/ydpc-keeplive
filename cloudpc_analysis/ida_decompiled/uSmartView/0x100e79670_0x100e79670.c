// 0x100e79670 @ 0x100e79670
__int64 __fastcall ikcp_update_judge_kcp(__int64 a1)
{
  if ( *(_BYTE *)(a1 + 12408) && *(_BYTE *)(a1 + 18456) && *(_DWORD *)(a1 + 96) - *(_DWORD *)(a1 + 12420) >= 80LL ) /*0x100e796c9*/
  {
    ikcp_set_auth_data( /*0x100e7974b*/
      a1,
      a1 + 320,
      *(_WORD *)(a1 + 18458),
      *(_WORD *)(a1 + 18460),
      *(_DWORD *)(a1 + 18464),
      *(_BYTE *)(a1 + 12407),
      *(_BYTE *)(a1 + 12452),
      *(_BYTE *)(a1 + 18469));
    return 0; /*0x100e79813*/
  }
  if ( *(_BYTE *)(a1 + 12408) /*0x100e797af*/
    && !*(_BYTE *)(a1 + 18456)
    && !*(_BYTE *)(a1 + 12410)
    && *(_DWORD *)(a1 + 96) - *(_DWORD *)(a1 + 12420) >= 80LL )
  {
    ikcp_send_link_sync( /*0x100e797f8*/
      a1,
      *(_BYTE *)(a1 + 12407),
      *(_BYTE *)(a1 + 12452),
      *(_BYTE *)(a1 + 18469),
      *(_BYTE *)(a1 + 18470));
    return 0; /*0x100e797fd*/
  }
  return 1; /*0x100e7981d*/
}
