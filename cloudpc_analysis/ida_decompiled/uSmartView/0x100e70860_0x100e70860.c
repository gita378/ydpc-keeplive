// 0x100e70860 @ 0x100e70860
__int64 __fastcall ice_deal_udt_auth(__int64 a1, __int64 a2, unsigned __int16 a3)
{
  __int64 v3; // rax
  __int64 v4; // rdi
  __int64 v5; // rsi
  __int64 v6; // rdx
  __int64 v7; // rcx
  __int64 v8; // r8
  __int64 v9; // r9
  int v10; // r9d
  __int64 v12; // [rsp+30h] [rbp-4D0h]
  __int64 v13; // [rsp+38h] [rbp-4C8h]
  _BYTE v16[1024]; // [rsp+70h] [rbp-490h] BYREF
  _BYTE __b[136]; // [rsp+470h] [rbp-90h] BYREF

  memset(__b, 0, 0x80u); /*0x100e708a1*/
  if ( a3 >= 0x47uLL ) /*0x100e708b3*/
  {
    if ( g_auth_type ) /*0x100e708f7*/
    {
      memset(v16, 0, sizeof(v16)); /*0x100e70a71*/
      v12 = *(unsigned __int16 *)(a1 + 18458) + a1 + 320; /*0x100e70a98*/
      tn_deal_aes_code( /*0x100e70ad8*/
        (unsigned int)g_passwd,
        1024,
        (unsigned int)v16,
        *(_DWORD *)(a1 + 18464),
        *(_DWORD *)(a2 + 31),
        0,
        0);
      ZXMemcpy(v12 + 126, *(unsigned __int16 *)(v12 + 124), v16, *(unsigned __int16 *)(v12 + 124)); /*0x100e70b0e*/
      tn_deal_aes_code(v12 + 60, 32, (unsigned int)__b, *(_DWORD *)(a1 + 18464), *(_DWORD *)(a2 + 31), 0, 0); /*0x100e70b5f*/
      v4 = v12 + 60; /*0x100e70b72*/
      v5 = 32; /*0x100e70b7f*/
      ZXMemcpy(v12 + 60, 32, __b, 32); /*0x100e70b85*/
    }
    else
    {
      v13 = *(unsigned __int16 *)(a1 + 18458) + a1 + 320; /*0x100e7091e*/
      v3 = ZXStrlen(v13 + 124, 64); /*0x100e7094f*/
      xor_with_key(v13 + 124, v3, 99); /*0x100e70963*/
      tn_deal_aes_code(v13 + 124, 64, (unsigned int)__b, *(_DWORD *)(a1 + 18464), *(_DWORD *)(a2 + 31), 0, 0); /*0x100e709a6*/
      ZXMemcpy(v13 + 124, 64, __b, 64); /*0x100e709cd*/
      tn_deal_aes_code(v13 + 60, 64, (unsigned int)__b, *(_DWORD *)(a1 + 18464), *(_DWORD *)(a2 + 31), 0, 0); /*0x100e70a1e*/
      v4 = v13 + 60; /*0x100e70a31*/
      v5 = 64; /*0x100e70a3e*/
      ZXMemcpy(v13 + 60, 64, __b, 64); /*0x100e70a44*/
    }
    if ( (unsigned int)spice_util_get_debug(v4, v5, v6, v7, v8, v9) && spice_gtk_log_level < 1 ) /*0x100e70ba7*/
      g_log( /*0x100e70bcf*/
        (unsigned int)"GSpice",
        128,
        (unsigned int)"[%-38s:%4d] ice_deal_udt_auth DONE!!",
        (unsigned int)"ice_deal_udt_auth",
        3439,
        v10);
    return 200; /*0x100e70bd9*/
  }
  else
  {
    return 404; /*0x100e708b9*/
  }
}
