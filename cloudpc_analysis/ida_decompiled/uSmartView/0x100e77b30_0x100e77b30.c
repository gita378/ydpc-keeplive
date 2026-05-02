// 0x100e77b30 @ 0x100e77b30
__int64 __fastcall ikcp_input(_DWORD *a1, unsigned __int8 *a2, __int64 a3, __int64 a4, int a5, int a6)
{
  char v7; // [rsp+48h] [rbp-F8h]
  unsigned __int8 v8; // [rsp+49h] [rbp-F7h] BYREF
  __int16 v9; // [rsp+4Ah] [rbp-F6h] BYREF
  unsigned __int16 v10; // [rsp+4Ch] [rbp-F4h] BYREF
  unsigned __int16 v11; // [rsp+4Eh] [rbp-F2h] BYREF
  int v12; // [rsp+50h] [rbp-F0h] BYREF
  unsigned int v13; // [rsp+54h] [rbp-ECh] BYREF
  int v14; // [rsp+58h] [rbp-E8h] BYREF
  int v15; // [rsp+5Ch] [rbp-E4h] BYREF
  __int64 v16; // [rsp+60h] [rbp-E0h]
  unsigned __int8 v17; // [rsp+6Bh] [rbp-D5h] BYREF
  unsigned int v18; // [rsp+6Ch] [rbp-D4h]
  int v19; // [rsp+70h] [rbp-D0h] BYREF
  int v20; // [rsp+74h] [rbp-CCh] BYREF
  unsigned int v21; // [rsp+78h] [rbp-C8h] BYREF
  unsigned int v22; // [rsp+7Ch] [rbp-C4h]
  __int64 v23; // [rsp+80h] [rbp-C0h] BYREF
  unsigned __int8 *v24; // [rsp+88h] [rbp-B8h] BYREF
  _DWORD *v25; // [rsp+90h] [rbp-B0h]
  int *v27; // [rsp+A0h] [rbp-A0h]
  unsigned __int8 *v28; // [rsp+A8h] [rbp-98h]
  unsigned __int8 *v29; // [rsp+B0h] [rbp-90h]
  _BYTE *v30; // [rsp+B8h] [rbp-88h]
  unsigned __int16 *v31; // [rsp+C0h] [rbp-80h]
  unsigned __int8 *v32; // [rsp+C8h] [rbp-78h]
  int *v33; // [rsp+D0h] [rbp-70h]
  unsigned __int8 *v34; // [rsp+D8h] [rbp-68h]
  int *v35; // [rsp+E0h] [rbp-60h]
  unsigned __int8 *v36; // [rsp+E8h] [rbp-58h]
  unsigned int *v37; // [rsp+F0h] [rbp-50h]
  unsigned __int8 *v38; // [rsp+F8h] [rbp-48h]
  unsigned __int16 *v39; // [rsp+100h] [rbp-40h]
  unsigned __int8 *v40; // [rsp+108h] [rbp-38h]
  unsigned __int8 *v41; // [rsp+110h] [rbp-30h]
  _BYTE *v42; // [rsp+118h] [rbp-28h]

  v25 = a1; /*0x100e77b42*/
  v24 = a2; /*0x100e77b49*/
  v23 = a3; /*0x100e77b50*/
  v22 = a1[9]; /*0x100e77b61*/
  v21 = 0; /*0x100e77b67*/
  v20 = 0; /*0x100e77b71*/
  v18 = 0; /*0x100e77b7b*/
  ikcp_log((_DWORD)a1, 2, (unsigned int)"[RI] %ld bytes", a3, a5, a6); /*0x100e77ba1*/
  a1[3105] = a1[24]; /*0x100e77bb7*/
  v25[3106] = ice_get_ms() - v25[3107]; /*0x100e77bd9*/
  v7 = 1; /*0x100e77be9*/
  if ( v24 ) /*0x100e77bef*/
  {
    v7 = 1; /*0x100e77c01*/
    if ( (int)v23 >= 21 ) /*0x100e77c07*/
      v7 = ~(*((_BYTE *)v25 + 12409) != 0); /*0x100e77c21*/
  }
  if ( (v7 & 1) != 0 ) /*0x100e77c36*/
  {
    return (unsigned int)-1; /*0x100e77c3c*/
  }
  else
  {
    while ( 1 ) /*0x100e77c55*/
    {
      v9 = 0; /*0x100e77c55*/
      v17 = 0; /*0x100e77c5e*/
      v16 = 0; /*0x100e77c65*/
      if ( v23 < 21 ) /*0x100e77c78*/
        break; /*0x100e77c78*/
      v19 = 21; /*0x100e77c83*/
      v28 = v24; /*0x100e77c94*/
      v27 = &v12; /*0x100e77ca2*/
      v12 = *(_DWORD *)v24; /*0x100e77cb9*/
      v28 = v24 + 4; /*0x100e77cc8*/
      v24 += 4; /*0x100e77cd6*/
      if ( v12 != v25[4] ) /*0x100e77cfd*/
        return (unsigned int)-1; /*0x100e77d0d*/
      v29 = &v8; /*0x100e77d2c*/
      v30 = v24 + 1; /*0x100e77d44*/
      v8 = *v24++; /*0x100e77d54*/
      v32 = v24; /*0x100e77d6b*/
      v31 = &v11; /*0x100e77d76*/
      v11 = *(_WORD *)v24; /*0x100e77d85*/
      v32 = v24 + 2; /*0x100e77d92*/
      v24 += 2; /*0x100e77d9a*/
      v34 = v24; /*0x100e77da8*/
      v33 = &v15; /*0x100e77db3*/
      v15 = *(_DWORD *)v24; /*0x100e77dc1*/
      v34 = v24 + 4; /*0x100e77dcd*/
      v24 += 4; /*0x100e77dd5*/
      v36 = v24; /*0x100e77de3*/
      v35 = &v14; /*0x100e77dee*/
      v14 = *(_DWORD *)v24; /*0x100e77dfc*/
      v36 = v24 + 4; /*0x100e77e08*/
      v24 += 4; /*0x100e77e10*/
      v38 = v24; /*0x100e77e1e*/
      v37 = &v13; /*0x100e77e29*/
      v13 = *(_DWORD *)v24; /*0x100e77e37*/
      v38 = v24 + 4; /*0x100e77e43*/
      v24 += 4; /*0x100e77e4b*/
      v40 = v24; /*0x100e77e59*/
      v39 = &v10; /*0x100e77e64*/
      v10 = *(_WORD *)v24; /*0x100e77e73*/
      v40 = v24 + 2; /*0x100e77e80*/
      v24 += 2; /*0x100e77e88*/
      if ( !v10 || v10 == 0xFFFF ) /*0x100e77eab*/
      {
        if ( v10 ) /*0x100e77ecf*/
          v10 = -1; /*0x100e77ee3*/
        else
          v10 = 0; /*0x100e77ed5*/
      }
      judge_kcp_be_fec( /*0x100e77f4c*/
        (_DWORD)v25,
        (unsigned int)&v24,
        (unsigned int)&v23,
        (unsigned int)&v9,
        v8,
        (unsigned int)&v19,
        v11,
        v10);
      if ( *((_BYTE *)v25 + 25232) ) /*0x100e77f58*/
      {
        v41 = &v17; /*0x100e77f77*/
        v42 = v24 + 1; /*0x100e77f89*/
        v17 = *v24++; /*0x100e77f93*/
        --v23; /*0x100e77fad*/
        if ( v17 ) /*0x100e77fbb*/
        {
          v16 = *(_QWORD *)&v25[2 * v17 + 5792]; /*0x100e77fd9*/
          if ( !v16 ) /*0x100e77fe8*/
            return (unsigned int)-1; /*0x100e77ff8*/
        }
      }
      sub_100E78200(v25, v16, v11, v8); /*0x100e78026*/
      if ( (int)sub_100E76A90(v25, v13, v16) > 0 ) /*0x100e78047*/
        v18 = 1; /*0x100e7804d*/
      if ( !v21 ) /*0x100e7805e*/
        v21 = v13 - 1; /*0x100e7806d*/
      sub_100E76CC0(v25, v16); /*0x100e78081*/
      if ( (unsigned int)judge_cmd_type( /*0x100e78148*/
                           (_DWORD)v25,
                           (_DWORD)v24,
                           (unsigned int)&v20,
                           (unsigned int)&v21,
                           v8,
                           v14,
                           v13,
                           v15,
                           v11,
                           v10,
                           v9,
                           v16) == -3 )
        return (unsigned int)-3; /*0x100e78158*/
      v24 += v10; /*0x100e78171*/
      v23 -= v10; /*0x100e7818b*/
    }
    if ( v20 ) /*0x100e7819e*/
      sub_100E78290(v25, v21); /*0x100e781b1*/
    split_ikcp_input(v25, v21, v22); /*0x100e781c9*/
    is_ikcp_push(v18, v25); /*0x100e781db*/
    return 0; /*0x100e781e0*/
  }
}
