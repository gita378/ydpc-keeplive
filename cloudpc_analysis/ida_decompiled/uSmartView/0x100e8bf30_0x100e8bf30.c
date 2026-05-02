// 0x100e8bf30 @ 0x100e8bf30
__int64 __fastcall sub_100E8BF30(__int64 a1, __int64 a2, unsigned int a3)
{
  __int64 v5; // [rsp+20h] [rbp-40h]
  __int64 v6; // [rsp+30h] [rbp-30h]
  __int64 v7; // [rsp+38h] [rbp-28h]

  if ( a1 ) /*0x100e8bf4b*/
  {
    v7 = *(_QWORD *)(a1 + 176); /*0x100e8bf6f*/
    if ( v7 && *(_QWORD *)(v7 + 304) ) /*0x100e8bf82*/
    {
      update_upward_bandwitdh_statistics(a1, (int)a3); /*0x100e8bf98*/
      v6 = *(_QWORD *)(v7 + 304); /*0x100e8bfa8*/
      if ( (*(_DWORD *)(v6 + 40) & 0x10) != 0 ) /*0x100e8bfb9*/
      {
        return 0; /*0x100e8bfbf*/
      }
      else
      {
        if ( *(_QWORD *)(v6 + 112) ) /*0x100e8bfcf*/
          v5 = *(_QWORD *)(v6 + 112); /*0x100e8bfe2*/
        else
          v5 = v7; /*0x100e8bfef*/
        if ( v5 == v7 ) /*0x100e8c01c*/
          return (unsigned int)sub_100E9B1E0(v5, a2, a3, 0); /*0x100e8c04e*/
        else
          return (unsigned int)sub_100E9B1E0(v5, a2, a3, a1); /*0x100e8c02a*/
      }
    }
    else
    {
      update_upward_bandwitdh_statistics(a1, (int)a3); /*0x100e8c069*/
      if ( (unsigned __int16)send_tcp_data_with_cache(a1, a2, a3) ) /*0x100e8c079*/
        return 0; /*0x100e8c096*/
      else
        return a3; /*0x100e8c08e*/
    }
  }
  else
  {
    return 0; /*0x100e8bf51*/
  }
}
