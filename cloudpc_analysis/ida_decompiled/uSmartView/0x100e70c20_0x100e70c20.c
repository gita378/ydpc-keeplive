// 0x100e70c20 @ 0x100e70c20
__int64 __fastcall ice_deal_udt_auth_res(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  unsigned int *v7; // [rsp+8h] [rbp-28h]

  if ( (unsigned __int16)a3 >= 0x39uLL ) /*0x100e70c3e*/
  {
    v7 = (unsigned int *)(a2 + 21); /*0x100e70c5a*/
    if ( (unsigned int)spice_util_get_debug(a1, a2, a3, (unsigned __int16)a3, a5, a6) && spice_gtk_log_level < 2 ) /*0x100e70c76*/
      g_log( /*0x100e70ca5*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] ice_deal_udt_auth_res retcode[%d]!!",
        (unsigned int)"ice_deal_udt_auth_res",
        3450,
        *v7);
    return *v7; /*0x100e70cb5*/
  }
  else
  {
    return 406; /*0x100e70c44*/
  }
}
