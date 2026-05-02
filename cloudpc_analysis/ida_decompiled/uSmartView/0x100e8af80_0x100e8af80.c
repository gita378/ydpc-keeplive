// 0x100e8af80 @ 0x100e8af80
__int64 __fastcall sub_100E8AF80(__int64 a1, unsigned int a2, __int64 a3)
{
  __int64 type; // rax
  __int64 v4; // rax
  __int64 v6; // [rsp+8h] [rbp-118h]
  __int64 v7; // [rsp+28h] [rbp-F8h]
  int connect_processtrack_id; // [rsp+34h] [rbp-ECh]
  __int64 v9; // [rsp+48h] [rbp-D8h]
  _WORD __b[84]; // [rsp+70h] [rbp-B0h] BYREF

  v7 = *(_QWORD *)(a1 + 264); /*0x100e8afbb*/
  type = spice_session_get_type(); /*0x100e8afc2*/
  v9 = g_type_instance_get_private(v7, type); /*0x100e8afdf*/
  memset(__b, 0, 0x9Eu); /*0x100e8aff8*/
  LOBYTE(__b[0]) = 26; /*0x100e8b012*/
  HIBYTE(__b[0]) = a2; /*0x100e8b022*/
  __b[1] = 154; /*0x100e8b02d*/
  ZXMemcpy(&__b[2], 154, a3, 154); /*0x100e8b066*/
  sub_100E9A620(a1, &__b[2]); /*0x100e8b07f*/
  update_bw_ctrl_socks_array_state(a1, 0); /*0x100e8b08d*/
  if ( *(_WORD *)(a1 + 396) == 1 ) /*0x100e8b0a7*/
  {
    connect_processtrack_id = spice_processtrack_get_connect_processtrack_id(*(_QWORD *)(a1 + 264)); /*0x100e8b0c0*/
    spice_processtrack_get_serial_num(*(_QWORD *)(v9 + 8LL * connect_processtrack_id + 2848), &__b[14], 16); /*0x100e8b0f2*/
    if ( (spice_session_is_emergency_key(*(_QWORD *)(a1 + 264)) & 1) != 0 /*0x100e8b162*/
      && !strcmp(*(const char **)(v9 + 2656), "rap")
      && !*(_DWORD *)(v9 + 160)
      && *(_QWORD *)(v9 + 2576) )
    {
      v6 = *(_QWORD *)(v9 + 2576); /*0x100e8b1a5*/
      v4 = ZXStrlen(v6, 36); /*0x100e8b1ac*/
      ZXMemcpy(&__b[22], 36, v6, v4); /*0x100e8b1c7*/
      HIBYTE(__b[40]) = 1; /*0x100e8b1d3*/
      LOBYTE(__b[41]) = 1; /*0x100e8b1de*/
    }
  }
  if ( *(int *)(a1 + 52) < 0 ) /*0x100e8b1f7*/
  {
    if ( (int)sub_100E8BF30(*(_QWORD *)(a1 + 200), __b, 158) <= 0 ) /*0x100e8b246*/
    {
      return 0; /*0x100e8b274*/
    }
    else
    {
      sub_100E9A950(a1, a2, a3); /*0x100e8b260*/
      return 1; /*0x100e8b265*/
    }
  }
  else
  {
    sub_100E8BA10(a1, __b, 158); /*0x100e8b210*/
    return 1; /*0x100e8b215*/
  }
}
