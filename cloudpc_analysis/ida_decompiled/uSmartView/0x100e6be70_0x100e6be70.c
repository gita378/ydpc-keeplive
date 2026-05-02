// 0x100e6be70 @ 0x100e6be70
__int64 __fastcall ice_deal_udp_read(__int64 a1)
{
  unsigned __int16 v1; // ax
  unsigned __int16 v2; // ax
  unsigned __int16 v3; // ax
  unsigned __int16 v4; // ax
  char *v6; // [rsp+8h] [rbp-168h]
  unsigned int v7; // [rsp+10h] [rbp-160h]
  unsigned int v8; // [rsp+14h] [rbp-15Ch]
  __int64 v9; // [rsp+18h] [rbp-158h]
  char *v10; // [rsp+28h] [rbp-148h]
  unsigned int v11; // [rsp+30h] [rbp-140h]
  unsigned int v12; // [rsp+34h] [rbp-13Ch]
  __int64 v13; // [rsp+38h] [rbp-138h]
  unsigned int v14; // [rsp+48h] [rbp-128h]
  unsigned int v15; // [rsp+4Ch] [rbp-124h]
  __int64 v16; // [rsp+50h] [rbp-120h]
  unsigned int v17; // [rsp+68h] [rbp-108h]
  unsigned int v18; // [rsp+6Ch] [rbp-104h]
  __int64 v19; // [rsp+70h] [rbp-100h]
  int v20; // [rsp+B8h] [rbp-B8h] BYREF
  socklen_t v21; // [rsp+C0h] [rbp-B0h] BYREF
  socklen_t v22; // [rsp+C4h] [rbp-ACh] BYREF
  sockaddr v23; // [rsp+C8h] [rbp-A8h] BYREF
  unsigned int v24; // [rsp+E4h] [rbp-8Ch]
  int v25; // [rsp+E8h] [rbp-88h]
  int v26; // [rsp+ECh] [rbp-84h]
  __int64 v27; // [rsp+F0h] [rbp-80h]
  __int64 v28; // [rsp+F8h] [rbp-78h]
  char v29[16]; // [rsp+100h] [rbp-70h] BYREF
  char __b[72]; // [rsp+110h] [rbp-60h] BYREF
  sockaddr v31; // [rsp+158h] [rbp-18h] BYREF

  v28 = a1; /*0x100e6be8b*/
  v27 = a1; /*0x100e6be93*/
  v25 = 0; /*0x100e6be97*/
  v22 = 16; /*0x100e6bea1*/
  v21 = 28; /*0x100e6beab*/
  ZXMemset(&v31, 16, 0, 16); /*0x100e6bec7*/
  ZXMemset(&v23, 28, 0, 28); /*0x100e6bee6*/
  memset(__b, 0, 0x40u); /*0x100e6beff*/
  while ( ++v25 < 10 ) /*0x100e6bf0d*/
  {
    if ( g_bDestIPV6 ) /*0x100e6bf23*/
      v26 = recvfrom(*(_DWORD *)(v27 + 16), (void *)(v27 + 172), 0x1000u, 0, &v23, &v21); /*0x100e6bf68*/
    else
      v26 = recvfrom(*(_DWORD *)(v27 + 16), (void *)(v27 + 172), 0x1000u, 0, &v31, &v22); /*0x100e6bfaf*/
    if ( v26 >= 21 ) /*0x100e6bfbc*/
    {
      memset(v29, 0, sizeof(v29)); /*0x100e6bfdf*/
      v20 = *(_DWORD *)&v31.sa_data[2]; /*0x100e6bfe7*/
      inet_ntop(2, &v20, v29, 0x10u); /*0x100e6c008*/
      sub_100E67150(*(unsigned __int16 *)v31.sa_data); /*0x100e6c011*/
      v24 = ikcp_getconv((unsigned int *)(v28 + 172)); /*0x100e6c04b*/
      if ( (IKCP_CONV_FLAG & v24) != 0 ) /*0x100e6c05c*/
      {
        if ( g_bDestIPV6 ) /*0x100e6c06e*/
        {
          inet_ntop(30, &v23.sa_data[6], __b, 0x40u); /*0x100e6c092*/
          if ( ikcp_be_spical_conv(v24) ) /*0x100e6c0a4*/
          {
            v19 = v28; /*0x100e6c0cd*/
            v18 = v26; /*0x100e6c0d4*/
            v17 = v24; /*0x100e6c0da*/
            v1 = sub_100E67150(*(unsigned __int16 *)v23.sa_data); /*0x100e6c0e7*/
            ice_deal_spical_cmd(v19, v18, v17, __b, v1); /*0x100e6c131*/
          }
          else
          {
            v16 = v28; /*0x100e6c156*/
            v15 = v26; /*0x100e6c15d*/
            v14 = v24; /*0x100e6c163*/
            v2 = sub_100E67150(*(unsigned __int16 *)v23.sa_data); /*0x100e6c170*/
            ice_deal_kcp_common_data(v16, v15, v14, (__int64)__b, v2); /*0x100e6c1ba*/
          }
        }
        else if ( ikcp_be_spical_conv(v24) ) /*0x100e6c1ca*/
        {
          v13 = v28; /*0x100e6c1eb*/
          v12 = v26; /*0x100e6c1f4*/
          v11 = v24; /*0x100e6c1fa*/
          v10 = inet_ntoa(*(in_addr *)&v31.sa_data[2]); /*0x100e6c205*/
          v3 = sub_100E67150(*(unsigned __int16 *)v31.sa_data); /*0x100e6c210*/
          ice_deal_spical_cmd(v13, v12, v11, v10, v3); /*0x100e6c25a*/
        }
        else
        {
          v9 = v28; /*0x100e6c277*/
          v8 = v26; /*0x100e6c280*/
          v7 = v24; /*0x100e6c286*/
          v6 = inet_ntoa(*(in_addr *)&v31.sa_data[2]); /*0x100e6c291*/
          v4 = sub_100E67150(*(unsigned __int16 *)v31.sa_data); /*0x100e6c29c*/
          ice_deal_kcp_common_data(v9, v8, v7, (__int64)v6, v4); /*0x100e6c2e6*/
        }
      }
    }
  }
  return 0; /*0x100e6c30f*/
}
