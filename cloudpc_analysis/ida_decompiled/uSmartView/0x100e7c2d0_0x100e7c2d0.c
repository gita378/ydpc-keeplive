// 0x100e7c2d0 @ 0x100e7c2d0
__int64 __fastcall ikcp_deal_clt_sync_ack(__int64 a1, __int64 a2)
{
  _DWORD __b[24]; // [rsp+10h] [rbp-70h] BYREF
  __int64 v4; // [rsp+70h] [rbp-10h]
  __int64 v5; // [rsp+78h] [rbp-8h]

  v5 = a1; /*0x100e7c2dd*/
  v4 = a2; /*0x100e7c2e1*/
  memset(__b, 0, sizeof(__b)); /*0x100e7c2fa*/
  ikcp_get_seg_info(a2, __b); /*0x100e7c307*/
  if ( __b[6] < 0x3E8u ) /*0x100e7c313*/
    sub_100E7C120(v5, __b[6]); /*0x100e7c320*/
  return 0; /*0x100e7c327*/
}
