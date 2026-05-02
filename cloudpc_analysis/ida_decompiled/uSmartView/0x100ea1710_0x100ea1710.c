// 0x100ea1710 @ 0x100ea1710
__int64 __fastcall sub_100EA1710(__int64 a1, signed int a2, int a3, __int64 a4, unsigned __int16 a5)
{
  __int64 v5; // rdx
  __int64 v6; // rcx
  __int64 v7; // r8
  __int64 v8; // r9
  __int64 v9; // rdi
  __int64 v10; // rdx
  __int64 v11; // rcx
  __int64 v12; // r8
  __int64 v13; // r9
  __int64 v14; // rdx
  __int64 v15; // rcx
  __int64 v16; // r8
  __int64 v17; // r9
  __int64 v18; // rdx
  __int64 v19; // rcx
  __int64 v20; // r8
  __int64 v21; // r9
  int v22; // eax
  int v23; // esi
  int v24; // edi
  int v25; // eax
  int v26; // esi
  __int64 v28; // [rsp+0h] [rbp-80h]
  __int64 v29; // [rsp+8h] [rbp-78h]
  __int64 v30; // [rsp+10h] [rbp-70h]
  unsigned int proxy_conv; // [rsp+2Ch] [rbp-54h]
  unsigned int syn_id; // [rsp+30h] [rbp-50h]
  _BYTE v33[12]; // [rsp+34h] [rbp-4Ch]
  __int16 v34; // [rsp+46h] [rbp-3Ah]
  __int16 v35; // [rsp+48h] [rbp-38h]
  int v36; // [rsp+4Ch] [rbp-34h]
  unsigned int *v37; // [rsp+50h] [rbp-30h]
  signed int v41; // [rsp+6Ch] [rbp-14h]

  v41 = a2; /*0x100ea171f*/
  v37 = (unsigned int *)(a1 + 432); /*0x100ea1738*/
  v36 = a2; /*0x100ea173f*/
  while ( 1 ) /*0x100ea1749*/
  {
    v34 = 0; /*0x100ea1749*/
    *(_QWORD *)v33 = (unsigned int)ikcp_get_spical_cmd(a3); /*0x100ea175f*/
    syn_id = ikcp_get_syn_id((__int64)v37); /*0x100ea176b*/
    proxy_conv = ikcp_get_proxy_conv((__int64)v37); /*0x100ea1777*/
    if ( !(unsigned int)sub_100EA1B20(a1, *(unsigned int *)v33) ) /*0x100ea1781*/
    {
      if ( (unsigned int)spice_util_get_debug(a1, *(unsigned int *)v33, v5, v6, v7, v8) ) /*0x100ea1794*/
      {
        LODWORD(v29) = a5; /*0x100ea17dc*/
        g_log( /*0x100ea17e3*/
          (unsigned int)"GSpice",
          8,
          (unsigned int)"[%-38s:%4d] recv unknown cmd %d from:%s:%d",
          (unsigned int)"deal_kcp_special_cmd",
          6750,
          *(_DWORD *)v33,
          a4,
          v29);
      }
      return 1; /*0x100ea17f3*/
    }
    v9 = *(_QWORD *)(a1 + 232); /*0x100ea17fc*/
    *(_QWORD *)&v33[4] = sub_100EA1B70(v9, *(unsigned int *)v33, a4, a5, syn_id, proxy_conv); /*0x100ea181e*/
    if ( !*(_QWORD *)&v33[4] ) /*0x100ea1827*/
      break; /*0x100ea1827*/
    v41 = ikcp_check_udp_data(*(_BYTE **)&v33[4], (__int64)v37, v41); /*0x100ea183d*/
    if ( v41 <= 0 ) /*0x100ea1844*/
    {
      if ( (unsigned int)spice_util_get_debug(*(_QWORD *)&v33[4], v37, v14, v15, v16, v17) && spice_gtk_log_level < 3 ) /*0x100ea1867*/
        g_log( /*0x100ea1893*/
          (unsigned int)"GSpice",
          16,
          (unsigned int)"[%-38s:%4d] udt data check failed(%d)",
          (unsigned int)"deal_kcp_special_cmd",
          6757,
          v41);
      return 2; /*0x100ea18a3*/
    }
LABEL_23:
    v35 = sub_100EA1D10( /*0x100ea19bc*/
            a1,
            *(_DWORD *)v33,
            a4,
            a5,
            *(_DWORD *)&v33[4],
            (_DWORD)v37,
            v41,
            *(_QWORD *)(*(_QWORD *)&v33[4] + 304LL),
            v34);
    if ( v35 ) /*0x100ea1a11*/
      return (unsigned int)v35; /*0x100ea1a1e*/
    v22 = 0; /*0x100ea1a23*/
    v23 = 21; /*0x100ea1a38*/
    v24 = 21; /*0x100ea1a3d*/
    if ( *(_BYTE *)(*(_QWORD *)&v33[4] + 18469LL) ) /*0x100ea1a29*/
      v24 = 23; /*0x100ea1a3f*/
    v36 -= (*(_BYTE *)(*(_QWORD *)&v33[4] + 25232LL) != 0) + v24; /*0x100ea1a69*/
    if ( *(_BYTE *)(*(_QWORD *)&v33[4] + 18469LL) ) /*0x100ea1a74*/
      v23 = 23; /*0x100ea1a80*/
    if ( *(_BYTE *)(*(_QWORD *)&v33[4] + 25232LL) ) /*0x100ea1a87*/
      v22 = 1; /*0x100ea1a91*/
    if ( v36 >= v22 + v23 ) /*0x100ea1a99*/
    {
      v25 = 0; /*0x100ea1aa4*/
      v26 = 21; /*0x100ea1ab9*/
      if ( *(_BYTE *)(*(_QWORD *)&v33[4] + 18469LL) ) /*0x100ea1aaa*/
        v26 = 23; /*0x100ea1abe*/
      if ( *(_BYTE *)(*(_QWORD *)&v33[4] + 25232LL) ) /*0x100ea1ac5*/
        v25 = 1; /*0x100ea1ad4*/
      v37 = (unsigned int *)((char *)v37 + v25 + v26); /*0x100ea1ae3*/
      a3 = ikcp_getconv(v37); /*0x100ea1af0*/
      if ( ikcp_be_spical_conv(a3) ) /*0x100ea1af6*/
        continue; /*0x100ea1af6*/
    }
    return 0; /*0x100ea1b04*/
  }
  if ( *(_DWORD *)v33 != 1 ) /*0x100ea18b1*/
  {
    if ( (unsigned int)spice_util_get_debug(v9, *(unsigned int *)v33, v10, v11, v12, v13) && spice_gtk_log_level < 1 ) /*0x100ea18d4*/
    {
      LODWORD(v29) = a5; /*0x100ea191d*/
      LODWORD(v30) = syn_id; /*0x100ea1926*/
      g_log( /*0x100ea192d*/
        (unsigned int)"GSpice",
        128,
        (unsigned int)"[%-38s:%4d] recv cmd:%d from:%s:%d syn_id:0x%x, but not find kcp",
        (unsigned int)"deal_kcp_special_cmd",
        6762,
        *(_DWORD *)v33,
        a4,
        v29,
        v30);
    }
    return 2; /*0x100ea193d*/
  }
  *(_QWORD *)&v33[4] = deal_svr_new_session(a1, a4, a5); /*0x100ea1953*/
  if ( *(_QWORD *)&v33[4] ) /*0x100ea195b*/
  {
    v34 = 1; /*0x100ea19b6*/
    goto LABEL_23; /*0x100ea19b6*/
  }
  if ( (unsigned int)spice_util_get_debug(a1, a4, v18, v19, v20, v21) ) /*0x100ea1966*/
  {
    LODWORD(v28) = a5; /*0x100ea199c*/
    g_log( /*0x100ea19a1*/
      (unsigned int)"GSpice",
      8,
      (unsigned int)"[%-38s:%4d] create new session %s:%d failed",
      (unsigned int)"deal_kcp_special_cmd",
      6766,
      a4,
      v28);
  }
  return 12; /*0x100ea1b0e*/
}
