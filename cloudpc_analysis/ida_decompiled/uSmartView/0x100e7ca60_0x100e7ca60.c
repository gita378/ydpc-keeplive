// 0x100e7ca60 @ 0x100e7ca60
__int64 __fastcall ikcp_set_auth_data_res(__int64 a1, __int64 a2, unsigned __int16 a3)
{
  int v4; // [rsp+10h] [rbp-20h]

  if ( *(_BYTE *)(a1 + 18456) ) /*0x100e7ca78*/
  {
    *(_BYTE *)(a1 + 18456) = 0; /*0x100e7ca94*/
    v4 = (*(__int64 (__fastcall **)(__int64, __int64, _QWORD))(a1 + 27272))(a1, a2, a3); /*0x100e7cab4*/
    if ( v4 == 200 ) /*0x100e7cabe*/
    {
      ikcp_send_link_sync( /*0x100e7cb13*/
        a1,
        *(_BYTE *)(a1 + 12407),
        *(_BYTE *)(a1 + 12452),
        *(_BYTE *)(a1 + 18469),
        *(_BYTE *)(a1 + 18470));
      return 200; /*0x100e7cb18*/
    }
    else
    {
      return (unsigned __int16)v4; /*0x100e7cac7*/
    }
  }
  else
  {
    return 200; /*0x100e7ca85*/
  }
}
