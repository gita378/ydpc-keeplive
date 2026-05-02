// 0x100e79830 @ 0x100e79830
__int64 __fastcall ikcp_set_auth_data(
        __int64 a1,
        __int64 a2,
        __int16 a3,
        __int16 a4,
        int a5,
        char a6,
        char a7,
        char a8)
{
  int v8; // eax
  unsigned __int16 v10; // [rsp+14h] [rbp-68Ch]
  unsigned __int16 v11; // [rsp+16h] [rbp-68Ah]
  _DWORD __b[24]; // [rsp+18h] [rbp-688h] BYREF
  _BYTE *v13; // [rsp+78h] [rbp-628h]
  char v14; // [rsp+87h] [rbp-619h]
  int v15; // [rsp+88h] [rbp-618h]
  __int16 v16; // [rsp+8Ch] [rbp-614h]
  __int16 v17; // [rsp+8Eh] [rbp-612h]
  __int64 v18; // [rsp+90h] [rbp-610h]
  __int64 v19; // [rsp+98h] [rbp-608h]
  _BYTE v20[1512]; // [rsp+A0h] [rbp-600h] BYREF

  v19 = a1; /*0x100e7985d*/
  v18 = a2; /*0x100e79864*/
  v17 = a3; /*0x100e7986b*/
  v16 = a4; /*0x100e79872*/
  v15 = a5; /*0x100e79879*/
  v14 = a6; /*0x100e79880*/
  v13 = v20; /*0x100e79887*/
  memset(__b, 0, sizeof(__b)); /*0x100e798ad*/
  if ( v16 < 1477 && v16 < (int)*(unsigned __int16 *)(v19 + 24) && v17 < (int)*(unsigned __int16 *)(v19 + 24) ) /*0x100e798f3*/
  {
    if ( !*(_BYTE *)(v19 + 18456) ) /*0x100e79907*/
    {
      *(_BYTE *)(v19 + 18456) = 1; /*0x100e7991d*/
      *(_BYTE *)(v19 + 12408) = 1; /*0x100e7992b*/
      *(_BYTE *)(v19 + 12407) = v14; /*0x100e7993f*/
      *(_BYTE *)(v19 + 18469) = a8; /*0x100e7994f*/
      *(_BYTE *)(v19 + 12452) = a7; /*0x100e7995f*/
      *(_DWORD *)(v19 + 18464) = v15; /*0x100e79972*/
      ZXMemcpy(v19 + 320, 6000, v18, v16 + v17); /*0x100e799a7*/
      if ( !*(_BYTE *)(v19 + 12411) ) /*0x100e799b3*/
      {
        *(_WORD *)(v19 + 18460) = v16; /*0x100e799ce*/
        *(_WORD *)(v19 + 18458) = v17; /*0x100e799e3*/
        ZXMemcpy(v19 + 12455, 6000, v18, v17 + v16); /*0x100e79a1d*/
      }
    }
    if ( *(_BYTE *)(v19 + 18457) ) /*0x100e79a2e*/
    {
      __b[8] = *(_DWORD *)(v19 + 16); /*0x100e79a45*/
      v11 = *(_WORD *)(v19 + 18458); /*0x100e79a59*/
      v10 = *(_WORD *)(v19 + 18460); /*0x100e79a6e*/
      __b[4] = -2147483640; /*0x100e79a75*/
    }
    else
    {
      v11 = 0; /*0x100e79a84*/
      v10 = *(_WORD *)(v19 + 18458); /*0x100e79a9b*/
      __b[4] = -2147483642; /*0x100e79aa2*/
    }
    __b[7] = *(_DWORD *)(v19 + 12416); /*0x100e79ac4*/
    v8 = *(_DWORD *)(v19 + 96); /*0x100e79ad1*/
    *(_DWORD *)(v19 + 12420) = v8; /*0x100e79adb*/
    __b[6] = v8; /*0x100e79ae1*/
    LOBYTE(__b[5]) = 0; /*0x100e79ae7*/
    v13 = (_BYTE *)sub_100E74C10(0, v20, __b); /*0x100e79afa*/
    ZXMemcpy(v13, v10, v11 + v19 + 320, v10); /*0x100e79b3c*/
    sub_100E74F00(v19, v20, (unsigned int)v10 + 21); /*0x100e79b64*/
  }
  return __stack_chk_guard; /*0x100e79b80*/
}
