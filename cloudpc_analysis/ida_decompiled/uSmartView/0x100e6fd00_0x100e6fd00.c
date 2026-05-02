// 0x100e6fd00 @ 0x100e6fd00
__int64 __fastcall ice_deal_tcp_multi_link(__int64 a1, int a2, __int64 a3, unsigned int a4)
{
  __int64 v5; // [rsp+8h] [rbp-28h]

  if ( a2 || *(_QWORD *)(a1 + 312) ) /*0x100e6fd29*/
  {
    if ( a2 == 1 && *(_QWORD *)(a1 + 312) ) /*0x100e6fd56*/
    {
      sub_100E68A30(*(_QWORD *)(a1 + 312), a3, a4); /*0x100e6fd79*/
    }
    else if ( a2 == 2 && *(_QWORD *)(a1 + 312) ) /*0x100e6fd95*/
    {
      v5 = *(_QWORD *)(a1 + 312); /*0x100e6fdae*/
      *(_BYTE *)(v5 + 51) = 1; /*0x100e6fdb6*/
      *(_QWORD *)(v5 + 104) = 0; /*0x100e6fdbe*/
      *(_QWORD *)(a1 + 312) = 0; /*0x100e6fdca*/
      ice_set_socket_flag_ex(v5, 16, 2815); /*0x100e6fde3*/
    }
  }
  else
  {
    ice_deal_tcp_multi_tcp_link(a1); /*0x100e6fd3a*/
  }
  return 0; /*0x100e6fdf4*/
}
