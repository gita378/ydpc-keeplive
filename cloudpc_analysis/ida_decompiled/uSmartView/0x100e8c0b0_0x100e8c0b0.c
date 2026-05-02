// 0x100e8c0b0 @ 0x100e8c0b0
__int64 __fastcall deal_udt_cag_auth(__int64 a1, __int64 a2, unsigned __int16 a3)
{
  __int64 type; // rax
  __int64 v4; // rax
  __int64 v6; // [rsp+28h] [rbp-4E8h]
  __int64 v7; // [rsp+30h] [rbp-4E0h]
  __int64 v8; // [rsp+38h] [rbp-4D8h]
  __int64 v9; // [rsp+50h] [rbp-4C0h]
  __int64 v10; // [rsp+58h] [rbp-4B8h]
  _BYTE v13[1024]; // [rsp+80h] [rbp-490h] BYREF
  _BYTE __b[136]; // [rsp+480h] [rbp-90h] BYREF

  v10 = *(_QWORD *)(a1 + 304); /*0x100e8c0ec*/
  if ( v10 ) /*0x100e8c0fb*/
  {
    v6 = *(_QWORD *)(v10 + 264); /*0x100e8c142*/
    type = spice_session_get_type(); /*0x100e8c149*/
    v9 = g_type_instance_get_private(v6, type); /*0x100e8c15f*/
    memset(__b, 0, 0x80u); /*0x100e8c17d*/
    memset(v13, 0, sizeof(v13)); /*0x100e8c197*/
    if ( a3 >= 0x47u ) /*0x100e8c1a6*/
    {
      if ( (unsigned int)g_strcmp0(*(_QWORD *)(v9 + 2648), "1") && (unsigned int)g_strcmp0(*(_QWORD *)(v9 + 2648), "2") ) /*0x100e8c21c*/
      {
        v7 = *(unsigned __int16 *)(a1 + 18458) + a1 + 320; /*0x100e8c36d*/
        v4 = ZXStrlen(v7 + 124, 64); /*0x100e8c39e*/
        xor_with_key(v7 + 124, v4, 99); /*0x100e8c3b2*/
        tn_deal_aes_code(v7 + 124, 64, (unsigned int)v13, *(_DWORD *)(a1 + 18464), *(_DWORD *)(a2 + 31), 0, 0); /*0x100e8c3f5*/
        ZXMemcpy(v7 + 124, 64, v13, 64); /*0x100e8c41c*/
        tn_deal_aes_code(v7 + 60, 64, (unsigned int)__b, *(_DWORD *)(a1 + 18464), *(_DWORD *)(a2 + 31), 0, 0); /*0x100e8c46d*/
        ZXMemcpy(v7 + 60, 64, __b, 64); /*0x100e8c493*/
      }
      else
      {
        v8 = *(unsigned __int16 *)(a1 + 18458) + a1 + 320; /*0x100e8c256*/
        tn_deal_aes_code( /*0x100e8c297*/
          v8 + 126,
          *(unsigned __int16 *)(v8 + 124),
          (unsigned int)v13,
          *(_DWORD *)(a1 + 18464),
          *(_DWORD *)(a2 + 31),
          0,
          0);
        ZXMemcpy(v8 + 126, *(unsigned __int16 *)(v8 + 124), v13, *(unsigned __int16 *)(v8 + 124)); /*0x100e8c2cb*/
        tn_deal_aes_code(v8 + 60, 32, (unsigned int)__b, *(_DWORD *)(a1 + 18464), *(_DWORD *)(a2 + 31), 0, 0); /*0x100e8c31c*/
        ZXMemcpy(v8 + 60, 32, __b, 32); /*0x100e8c342*/
      }
      return 200; /*0x100e8c498*/
    }
    else
    {
      return 404; /*0x100e8c1ac*/
    }
  }
  else
  {
    g_return_if_fail_warning("GSpice", "deal_udt_cag_auth", "udp_sock != NULL"); /*0x100e8c11b*/
    return 1; /*0x100e8c120*/
  }
}
