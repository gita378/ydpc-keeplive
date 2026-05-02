// 0x100ea1d10 @ 0x100ea1d10
__int64 __fastcall sub_100EA1D10(
        __int64 a1,
        unsigned int a2,
        int a3,
        unsigned __int16 a4,
        __int64 a5,
        __int64 a6,
        int a7,
        __int64 a8,
        __int16 a9)
{
  __int16 v10; // [rsp+1Ch] [rbp-44h]

  v10 = sub_100EA1E00(a1, a2, a3, a4, a5, a6, a7); /*0x100ea1d70*/
  if ( v10 ) /*0x100ea1d77*/
  {
    set_fd_session_flag(a1, 16, 6721); /*0x100ea1d8b*/
    return (unsigned int)v10; /*0x100ea1d93*/
  }
  else
  {
    sub_100EA2220(a1, a2, a5, a6, (unsigned int)a9, a8); /*0x100ea1db7*/
    sub_100EA2590(a2, a5, a6, a8); /*0x100ea1dcf*/
    sub_100EA2790(a2, a5, a6, a8); /*0x100ea1de7*/
    return 0; /*0x100ea1dec*/
  }
}
