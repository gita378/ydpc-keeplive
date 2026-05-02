// 0x100e74f00 @ 0x100e74f00
__int64 __fastcall sub_100E74F00(const char *a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  int v6; // r8d
  int v7; // r9d
  unsigned int v9; // [rsp+4h] [rbp-1Ch]
  __int64 v10; // [rsp+8h] [rbp-18h]
  const char *v11; // [rsp+10h] [rbp-10h]

  v11 = a1; /*0x100e74f08*/
  v10 = a2; /*0x100e74f0c*/
  v9 = a3; /*0x100e74f10*/
  if ( !a1 && (unsigned int)spice_util_get_debug(0, a2, a3, a4, a5, a6) ) /*0x100e74f28*/
  {
    a1 = "GSpice"; /*0x100e74f36*/
    a2 = 8; /*0x100e74f3d*/
    g_log( /*0x100e74f5f*/
      (unsigned int)"GSpice",
      8,
      (unsigned int)"[%-38s:%4d] assertion `%s' failed",
      (unsigned int)"ikcp_output",
      493,
      (unsigned int)"kcp");
  }
  if ( !*((_QWORD *)v11 + 3406) && (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) ) /*0x100e74f94*/
    g_log( /*0x100e74fcb*/
      (unsigned int)"GSpice",
      8,
      (unsigned int)"[%-38s:%4d] assertion `%s' failed",
      (unsigned int)"ikcp_output",
      494,
      (unsigned int)"kcp->output");
  if ( (unsigned int)sub_100E74510(v11, 1) ) /*0x100e74fe8*/
    ikcp_log((_DWORD)v11, 1, (unsigned int)"[RO] %ld bytes", v9, v6, v7); /*0x100e7500c*/
  if ( v9 ) /*0x100e75015*/
  {
    if ( v11[12406] && v11[12409] ) /*0x100e7503f*/
    {
      sub_100E7C770(v10, v9); /*0x100e75056*/
      v9 += 4; /*0x100e75061*/
    }
    return (unsigned int)(*((__int64 (__fastcall **)(__int64, _QWORD, const char *, _QWORD))v11 + 3406))( /*0x100e75087*/
                           v10,
                           v9,
                           v11,
                           *((_QWORD *)v11 + 37));
  }
  else
  {
    return 0; /*0x100e7501b*/
  }
}
