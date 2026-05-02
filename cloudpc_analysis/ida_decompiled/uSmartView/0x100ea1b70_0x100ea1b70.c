// 0x100ea1b70 @ 0x100ea1b70
__int64 *__fastcall sub_100EA1B70(__int64 a1, __int64 a2, __int64 a3, unsigned __int16 a4, __int64 a5, __int64 a6)
{
  __int64 *v6; // rdx
  bool v8; // [rsp+13h] [rbp-3Dh]
  __int64 *i; // [rsp+18h] [rbp-38h]
  int v10; // [rsp+24h] [rbp-2Ch]
  int v11; // [rsp+28h] [rbp-28h]

  v11 = a5; /*0x100ea1b87*/
  v10 = a6; /*0x100ea1b8b*/
  v8 = 1; /*0x100ea1ba2*/
  if ( (_DWORD)a2 != 1 ) /*0x100ea1ba6*/
  {
    v8 = 1; /*0x100ea1bb6*/
    if ( (_DWORD)a2 != 2 ) /*0x100ea1bb9*/
    {
      v8 = 1; /*0x100ea1bc9*/
      if ( (_DWORD)a2 != 7 ) /*0x100ea1bcc*/
        v8 = (_DWORD)a2 == 9; /*0x100ea1bdd*/
    }
  }
  v6 = *(__int64 **)(a1 + 8264); /*0x100ea1bef*/
  for ( i = v6; i != (__int64 *)(a1 + 8264); i = (__int64 *)*i ) /*0x100ea1bf6*/
  {
    if ( v8 ) /*0x100ea1be3*/
    {
      v6 = (__int64 *)*((unsigned __int16 *)i + 6202); /*0x100ea1c24*/
      if ( a4 == (_DWORD)v6 && (_DWORD)a5 == *((_DWORD *)i + 3104) ) /*0x100ea1c40*/
        return i; /*0x100ea1c4e*/
    }
    else if ( (_DWORD)a5 == *((_DWORD *)i + 4) ) /*0x100ea1c62*/
    {
      ikcp_set_dest(i, a3, a4); /*0x100ea1c74*/
      return i; /*0x100ea1c81*/
    }
  }
  if ( (unsigned int)spice_util_get_debug(a1, a2, v6, a1 + 8264, a5, a6) && spice_gtk_log_level < 1 ) /*0x100ea1cbd*/
    g_log( /*0x100ea1cef*/
      (unsigned int)"GSpice",
      128,
      (unsigned int)"[%-38s:%4d] find kcp(syn_id = 0x%x, conv = 0x%x) failed",
      (unsigned int)"get_thread_kcp",
      6322,
      v11,
      v10);
  return 0; /*0x100ea1d05*/
}
