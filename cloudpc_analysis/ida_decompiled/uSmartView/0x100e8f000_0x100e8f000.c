// 0x100e8f000 @ 0x100e8f000
__int64 __fastcall deal_kcp_common_data(__int64 a1, unsigned int a2, int a3, __int64 a4, unsigned __int16 a5)
{
  __int64 v5; // rsi
  __int64 v6; // rdx
  __int64 v7; // rcx
  __int64 v8; // r8
  __int64 v9; // r9
  __int64 ms; // rax
  __int64 v11; // rdx
  __int64 v12; // r8
  __int64 v13; // r9
  __int64 v14; // rcx
  __int64 v15; // r8
  __int64 v16; // r9
  int v17; // r9d
  __int64 *v19; // [rsp+20h] [rbp-40h]
  __int64 *i; // [rsp+28h] [rbp-38h]
  __int64 v21; // [rsp+30h] [rbp-30h]
  int v23; // [rsp+4Ch] [rbp-14h]

  v19 = 0; /*0x100e8f02b*/
  for ( i = *(__int64 **)(*(_QWORD *)(a1 + 232) + 8264LL); /*0x100e8f045*/
        i != (__int64 *)(*(_QWORD *)(a1 + 232) + 8264LL);
        i = (__int64 *)*i )
  {
    if ( a3 == *((_DWORD *)i + 4) ) /*0x100e8f072*/
    {
      ikcp_set_dest(i, a4, a5); /*0x100e8f084*/
      v19 = i; /*0x100e8f08d*/
      break; /*0x100e8f091*/
    }
  }
  if ( !v19 ) /*0x100e8f0b3*/
    return 1; /*0x100e8f0bf*/
  v5 = a1 + 432; /*0x100e8f0d5*/
  v23 = ikcp_check_udp_data(v19, a1 + 432, a2); /*0x100e8f0dd*/
  if ( v23 <= 0 ) /*0x100e8f0e4*/
  {
    if ( (unsigned int)spice_util_get_debug(v19, v5, v6, v7, v8, v9) && spice_gtk_log_level < 3 ) /*0x100e8f107*/
      g_log( /*0x100e8f133*/
        (unsigned int)"GSpice",
        16,
        (unsigned int)"[%-38s:%4d] udt data check failed(%d)",
        (unsigned int)"deal_kcp_common_data",
        7406,
        v23);
    return 1; /*0x100e8f143*/
  }
  v21 = v19[38]; /*0x100e8f153*/
  ms = ice_get_ms(); /*0x100e8f159*/
  v14 = v21; /*0x100e8f15e*/
  *(_QWORD *)(v21 + 152) = ms; /*0x100e8f162*/
  if ( (unsigned __int64)(*(_QWORD *)(v21 + 152) - qword_1033461B0) >= 0x7D0 ) /*0x100e8f181*/
  {
    qword_1033461B0 = *(_QWORD *)(v21 + 152); /*0x100e8f192*/
    if ( (unsigned int)spice_util_get_debug(v19, v5, v11, v21, v12, v13) ) /*0x100e8f199*/
    {
      if ( spice_gtk_log_level < 1 ) /*0x100e8f1b1*/
        g_log( /*0x100e8f21c*/
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] conv:%u snd_nxt:%u, rcv_nxt:%u touch:%llu",
          (unsigned int)"deal_kcp_common_data",
          7414,
          *((_DWORD *)v19 + 4),
          *((_DWORD *)v19 + 10),
          *((_DWORD *)v19 + 11),
          *(_QWORD *)(v21 + 152),
          v19[5]);
    }
  }
  ikcp_input(v19, (unsigned __int8 *)(a1 + 432), v23, v14, v12, v13); /*0x100e8f240*/
  if ( !*(_QWORD *)(v21 + 112) || *(_BYTE *)(v21 + 129) ) /*0x100e8f258*/
  {
LABEL_26:
    if ( *((_BYTE *)v19 + 25232) ) /*0x100e8f303*/
      update_downward_bandwitdh_statistics(a1, v23); /*0x100e8f326*/
    else
      proxy_data_read(a1); /*0x100e8f314*/
    return 0; /*0x100e8f32b*/
  }
  if ( *(_QWORD *)(v21 + 216) ) /*0x100e8f26d*/
  {
    (*(void (__fastcall **)(__int64))(v21 + 216))(v21); /*0x100e8f289*/
    if ( !*(_BYTE *)(v21 + 129) ) /*0x100e8f2e0*/
      return 1; /*0x100e8f2f5*/
    goto LABEL_26; /*0x100e8f2e9*/
  }
  if ( (unsigned int)spice_util_get_debug(v19, a1 + 432, v21, 0, v15, v16) ) /*0x100e8f295*/
    g_log( /*0x100e8f2c5*/
      (unsigned int)"GSpice",
      8,
      (unsigned int)"[%-38s:%4d] udp_sock->read_func is NULL, cannot perform SSL read operation",
      (unsigned int)"deal_kcp_common_data",
      7422,
      v17);
  return 1; /*0x100e8f335*/
}
