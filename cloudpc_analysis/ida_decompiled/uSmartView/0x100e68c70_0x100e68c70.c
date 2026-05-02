// 0x100e68c70 @ 0x100e68c70
__int64 __fastcall ice_deal_cag_reply(__int64 a1)
{
  __int64 v1; // rdi
  __int64 v2; // rdx
  __int64 v3; // r8
  __int64 v4; // r9
  int v5; // r9d
  __int64 v6; // rdx
  __int64 v7; // r8
  __int64 v8; // r9
  int v10; // [rsp+8h] [rbp-1028h]
  unsigned int step_2_msg; // [rsp+Ch] [rbp-1024h]
  unsigned int v12; // [rsp+10h] [rbp-1020h] BYREF
  unsigned int v13; // [rsp+14h] [rbp-101Ch] BYREF
  __int64 v14; // [rsp+18h] [rbp-1018h]
  _BYTE __b[4104]; // [rsp+20h] [rbp-1010h] BYREF

  v14 = a1; /*0x100e68c8b*/
  memset(__b, 0, 0x1000u); /*0x100e68ca1*/
  if ( *(_BYTE *)(a1 + 34) == 1 ) /*0x100e68cb4*/
  {
    v1 = v14 + 172; /*0x100e68cc7*/
    if ( (unsigned int)cag_deal_replay_1(v14 + 172, &v13, &v12) ) /*0x100e68cd8*/
    {
      if ( (unsigned int)spice_util_get_debug(v1, &v13, v2, 0, v3, v4) && spice_gtk_log_level < 2 ) /*0x100e68d7e*/
        g_log( /*0x100e68da6*/
          (unsigned int)"GSpice",
          64,
          (unsigned int)"[%-38s:%4d] parse cag reply 1 failed",
          (unsigned int)"ice_deal_cag_reply",
          914,
          v5);
      ice_set_socket_flag_ex(v14, 16, 915); /*0x100e68dc1*/
    }
    else
    {
      step_2_msg = cag_get_step_2_msg(&g_cag_param, *(unsigned int *)(v14 + 36), v13, v12, __b, 4096); /*0x100e68d1d*/
      sub_100E68A30(v14, __b, step_2_msg); /*0x100e68d30*/
      *(_DWORD *)(v14 + 64) = 36; /*0x100e68d3c*/
      *(_DWORD *)(v14 + 60) = 0; /*0x100e68d4a*/
      *(_BYTE *)(v14 + 34) = 2; /*0x100e68d58*/
    }
  }
  else
  {
    v10 = cag_deal_replay_2(v14 + 172); /*0x100e68de2*/
    if ( v10 ) /*0x100e68dee*/
    {
      if ( (unsigned int)spice_util_get_debug(v14 + 172, 0, v6, 0, v7, v8) && spice_gtk_log_level < 2 ) /*0x100e68e67*/
        g_log( /*0x100e68e96*/
          (unsigned int)"GSpice",
          64,
          (unsigned int)"[%-38s:%4d] parse cag reply 2, init cag connection failed, err code:%d",
          (unsigned int)"ice_deal_cag_reply",
          933,
          v10);
      ice_set_socket_flag_ex(v14, 16, 934); /*0x100e68eb1*/
    }
    else
    {
      *(_DWORD *)(v14 + 64) = 12; /*0x100e68dfb*/
      *(_DWORD *)(v14 + 60) = 0; /*0x100e68e09*/
      *(_QWORD *)(v14 + 120) = ice_deal_udt_tcp_read; /*0x100e68e1e*/
      sub_100E69060(v14, 1); /*0x100e68e2e*/
      ice_send_bind_udt_msg(v14); /*0x100e68e40*/
    }
  }
  return 0; /*0x100e68ed5*/
}
