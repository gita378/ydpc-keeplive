// 0x100e7bc20 @ 0x100e7bc20
__int64 __fastcall ikcp_deal_svr_sync_ack(__int64 a1, __int64 a2)
{
  __int64 v2; // rax
  char v3; // al
  int v4; // r9d
  int v5; // r8d
  __int64 v6; // rcx
  __int64 v7; // rax
  int v8; // ecx
  int v9; // r8d
  int v10; // r9d
  int v11; // edx
  int v12; // r9d
  _DWORD __b[24]; // [rsp+18h] [rbp-B8h] BYREF
  __int64 seg_info; // [rsp+78h] [rbp-58h]
  __int64 v16; // [rsp+80h] [rbp-50h]
  int v17; // [rsp+88h] [rbp-48h]
  int v18; // [rsp+8Ch] [rbp-44h]
  _BYTE v19[56]; // [rsp+90h] [rbp-40h] BYREF

  v16 = a1; /*0x100e7bc3b*/
  seg_info = a2; /*0x100e7bc3f*/
  memset(__b, 0, sizeof(__b)); /*0x100e7bc5e*/
  seg_info = ikcp_get_seg_info(a2, __b); /*0x100e7bc73*/
  *(_DWORD *)(v16 + 16) = __b[8]; /*0x100e7bc82*/
  if ( *(_BYTE *)(v16 + 12406) ) /*0x100e7bc8a*/
    *(_BYTE *)(v16 + 12406) = (__b[5] & 8) != 0; /*0x100e7bcb7*/
  if ( *(_BYTE *)(v16 + 18469) ) /*0x100e7bcc1*/
  {
    *(_BYTE *)(v16 + 18469) = (__b[5] & 0x20) != 0; /*0x100e7bcee*/
    *(_WORD *)(v16 + 21104) = 2; /*0x100e7bcf8*/
  }
  if ( *(_BYTE *)(v16 + 12406) ) /*0x100e7bd05*/
    *(_WORD *)(v16 + 30) = *(_WORD *)(v16 + 24) - 4; /*0x100e7bd21*/
  if ( *(_BYTE *)(v16 + 18469) ) /*0x100e7bd29*/
  {
    *(_WORD *)(v16 + 30) = *(_WORD *)(v16 + 24) - 2; /*0x100e7bd49*/
    if ( !*(_QWORD *)(v16 + 18504) ) /*0x100e7bd51*/
    {
      v2 = ikcp_segment_new(v16, 1472); /*0x100e7bd67*/
      *(_QWORD *)(v16 + 18504) = v2; /*0x100e7bd74*/
      if ( *(_QWORD *)(v16 + 18504) ) /*0x100e7bd7f*/
      {
        *(_BYTE *)(v16 + 18474) = 20; /*0x100e7bd92*/
        ZXMemset( /*0x100e7bdc8*/
          *(_QWORD *)(*(_QWORD *)(v16 + 18504) + 88LL),
          *(unsigned __int16 *)(*(_QWORD *)(v16 + 18504) + 74LL),
          0,
          *(unsigned __int16 *)(*(_QWORD *)(v16 + 18504) + 74LL));
      }
    }
    sub_100E7C0A0(v16, *(unsigned __int8 *)(v16 + 18469)); /*0x100e7bde1*/
  }
  if ( *(_BYTE *)(v16 + 18470) ) /*0x100e7bdea*/
    *(_BYTE *)(v16 + 18470) = (__b[5] & 0x80) != 0; /*0x100e7be19*/
  v3 = ikcp_be_support_push_data_ex(__b); /*0x100e7be26*/
  *(_BYTE *)(v16 + 18468) = v3; /*0x100e7be2f*/
  sub_100E7BBA0(v16, *(_QWORD *)(v16 + 18504)); /*0x100e7be44*/
  __b[4] = -2147483646; /*0x100e7be49*/
  v5 = __b[6]; /*0x100e7be5a*/
  v18 = *(_DWORD *)(v16 + 96); /*0x100e7be61*/
  v17 = __b[6]; /*0x100e7be64*/
  v6 = v18 - __b[6]; /*0x100e7be6e*/
  if ( v6 < 0 ) /*0x100e7be75*/
  {
    __b[6] = 0; /*0x100e7bea2*/
  }
  else
  {
    __b[6] = *(_DWORD *)(v16 + 96) - __b[6]; /*0x100e7be88*/
    sub_100E7C120(v16, __b[6]); /*0x100e7be98*/
  }
  if ( (__b[5] & 0x10000) != 0 && !*(_QWORD *)(v16 + 21064) ) /*0x100e7bec3*/
  {
    v7 = sim_receiver_create(v16, 0); /*0x100e7beda*/
    v8 = v16; /*0x100e7bedf*/
    *(_QWORD *)(v16 + 21064) = v7; /*0x100e7bee3*/
    ikcp_info( /*0x100e7befe*/
      v16,
      (unsigned int)"server support GCC and client enable create. conv:[%u] ",
      *(_DWORD *)(v16 + 16),
      v8,
      v9,
      v10);
  }
  if ( *(_BYTE *)(v16 + 27244) ) /*0x100e7bf07*/
    *(_BYTE *)(v16 + 27245) = (__b[5] & 0x80000) != 0; /*0x100e7bf34*/
  LOBYTE(v6) = (__b[5] & 0x20000) != 0; /*0x100e7bf50*/
  *(_BYTE *)(v16 + 25232) = v6; /*0x100e7bf5a*/
  ikcp_info(v16, (unsigned int)"be_using_stream:[%d] ", *(unsigned __int8 *)(v16 + 25232), v6, v5, v4); /*0x100e7bf78*/
  v11 = 0; /*0x100e7bf7d*/
  v12 = 21; /*0x100e7bf95*/
  if ( *(_BYTE *)(v16 + 18469) ) /*0x100e7bf83*/
    v12 = 23; /*0x100e7bf9b*/
  if ( *(_BYTE *)(v16 + 25232) ) /*0x100e7bfa3*/
    v11 = 1; /*0x100e7bfb5*/
  *(_DWORD *)(v16 + 12336) = v11 + v12; /*0x100e7bfc0*/
  if ( *(_BYTE *)(v16 + 18470) && !*(_BYTE *)(v16 + 12409) && !*(_BYTE *)(v16 + 21108) ) /*0x100e7bff6*/
    (*(void (__fastcall **)(__int64, _QWORD, _QWORD, _QWORD))(v16 + 27280))(v16, 0, 0, 0); /*0x100e7c02c*/
  *(_BYTE *)(v16 + 12411) = 0; /*0x100e7c037*/
  *(_BYTE *)(v16 + 12409) = 1; /*0x100e7c042*/
  sub_100E74C10(v16, v19, __b); /*0x100e7c054*/
  sub_100E74F00(v16, v19, 21); /*0x100e7c06d*/
  return 0; /*0x100e7c08b*/
}
