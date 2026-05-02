// 0x100e8aac0 @ 0x100e8aac0
__int64 __fastcall sub_100E8AAC0(__int64 a1, int a2)
{
  if ( !a1 ) /*0x100e8aad4*/
    return g_return_if_fail_warning("GSpice", "set_clt_fd_session_priority", "in_sock != NULL"); /*0x100e8aaf4*/
  if ( a2 >= 1 && a2 <= 3 || a2 == 9 ) /*0x100e8ab1f*/
  {
    *(_BYTE *)(a1 + 44) = a2; /*0x100e8ab2c*/
    return (unsigned int)a2; /*0x100e8ab25*/
  }
  else
  {
    *(_BYTE *)(a1 + 44) = 3; /*0x100e8ab38*/
    return a1; /*0x100e8ab34*/
  }
}
