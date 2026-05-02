// 0x100e7b300 @ 0x100e7b300
__int64 __fastcall ikcp_check_udp_data(_BYTE *a1, __int64 a2, unsigned int a3)
{
  int v3; // eax
  int v4; // edi

  if ( a1 ) /*0x100e7b318*/
  {
    if ( a1[12406] && a1[12409] ) /*0x100e7b33f*/
    {
      v3 = 0; /*0x100e7b357*/
      v4 = 21; /*0x100e7b36f*/
      if ( a1[18469] ) /*0x100e7b360*/
        v4 = 23; /*0x100e7b374*/
      if ( a1[25232] ) /*0x100e7b37b*/
        v3 = 1; /*0x100e7b38a*/
      if ( (int)a3 >= v3 + v4 + 4 ) /*0x100e7b394*/
        return (unsigned int)sub_100E7B3C0(a2, a3); /*0x100e7b3b2*/
      else
        return (unsigned int)-2; /*0x100e7b39a*/
    }
    else
    {
      return a3; /*0x100e7b34f*/
    }
  }
  else
  {
    return (unsigned int)-2; /*0x100e7b31e*/
  }
}
