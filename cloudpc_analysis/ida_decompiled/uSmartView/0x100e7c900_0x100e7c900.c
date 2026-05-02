// 0x100e7c900 @ 0x100e7c900
__int64 __fastcall ikcp_set_auth_head_res(__int64 a1, __int64 a2, unsigned __int16 a3)
{
  int v3; // r8d
  int v4; // r9d
  int v6; // [rsp+28h] [rbp-28h]

  if ( *(_BYTE *)(a1 + 18457) )
  {
    return 200; /*0x100e7c926*/
  }
  else if ( *(_BYTE *)(a1 + 18456) )
  {
    *(_BYTE *)(a1 + 18457) = 1; /*0x100e7c951*/
    *(_DWORD *)(a1 + 16) = ikcp_get_proxy_conv(a2); /*0x100e7c965*/
    ikcp_info(a1, (unsigned int)"kcp:%p, conv value: %u", a1, *(_DWORD *)(a1 + 16), v3, v4);
    v6 = (*(__int64 (__fastcall **)(__int64, __int64, _QWORD))(a1 + 27264))(a1, a2, a3); /*0x100e7c9a9*/
    if ( v6 == 200 ) /*0x100e7c9b3*/
    {
      ikcp_set_auth_data( /*0x100e7ca41*/
        a1,
        a1 + 320,
        *(_WORD *)(a1 + 18458),
        *(_WORD *)(a1 + 18460),
        *(_DWORD *)(a1 + 18464),
        *(_BYTE *)(a1 + 12407),
        *(_BYTE *)(a1 + 12452),
        *(_BYTE *)(a1 + 18469));
      return 200; /*0x100e7ca46*/
    }
    else
    {
      return (unsigned __int16)v6; /*0x100e7c9bc*/
    }
  }
  else
  {
    return 404; /*0x100e7c942*/
  }
}
