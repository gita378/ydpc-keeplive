// 0x100e8ba10 @ 0x100e8ba10
__int64 __fastcall sub_100E8BA10(__int64 a1, __int64 a2, int a3)
{
  __int64 v4; // rdi
  __int64 v5; // rdx
  __int64 v6; // rcx
  __int64 v7; // r8
  __int64 v8; // r9
  int v9; // r9d
  __int64 v10; // rdi
  __int64 v11; // rsi
  __int64 v12; // rdx
  __int64 v13; // rcx
  __int64 v14; // r8
  __int64 v15; // r9
  __int64 v16; // rsi
  __int64 v17; // rdx
  __int64 v18; // rcx
  __int64 v19; // r8
  __int64 v20; // r9
  int v21; // r9d
  __int64 v22; // rdi
  __int64 v23; // rdx
  __int64 v24; // rcx
  __int64 v25; // r8
  __int64 v26; // r9
  int v27; // r9d
  int v28; // r9d
  void *v29; // rsi
  __int64 v30; // rdx
  __int64 v31; // rcx
  __int64 v32; // r8
  __int64 v33; // r9
  __int64 thread_proxy_fd_session; // [rsp+18h] [rbp-48h]
  __int64 v35; // [rsp+20h] [rbp-40h]
  __int64 v36; // [rsp+28h] [rbp-38h]
  _WORD __b[2]; // [rsp+30h] [rbp-30h] BYREF
  int v38; // [rsp+34h] [rbp-2Ch] BYREF
  __int64 v39; // [rsp+38h] [rbp-28h] BYREF
  void *v40; // [rsp+40h] [rbp-20h]
  int v41; // [rsp+4Ch] [rbp-14h]
  __int64 v42; // [rsp+50h] [rbp-10h]
  __int64 v43; // [rsp+58h] [rbp-8h]

  v43 = a1; /*0x100e8ba18*/
  v42 = a2; /*0x100e8ba1c*/
  v41 = a3; /*0x100e8ba20*/
  if ( !a2 ) /*0x100e8ba28*/
    return g_return_if_fail_warning("GSpice", "spice_session_write_port_data", "data != NULL"); /*0x100e8ba48*/
  if ( v41 <= 0 ) /*0x100e8ba60*/
    return g_return_if_fail_warning("GSpice", "spice_session_write_port_data", "data_len > 0"); /*0x100e8ba80*/
  v40 = 0; /*0x100e8ba91*/
  v39 = 0; /*0x100e8ba99*/
  v38 = 0; /*0x100e8baa1*/
  memset(__b, 0, sizeof(__b)); /*0x100e8bab4*/
  v35 = 0; /*0x100e8bac1*/
  v4 = *(_QWORD *)(v43 + 232); /*0x100e8bacd*/
  thread_proxy_fd_session = get_thread_proxy_fd_session(v4, 6); /*0x100e8bade*/
  if ( thread_proxy_fd_session )
  {
    spice_session_channels_mutex_lock(*(_QWORD *)(v43 + 264)); /*0x100e8bb4f*/
    v10 = *(_QWORD *)(v43 + 264); /*0x100e8bb58*/
    v11 = *(unsigned int *)(v43 + 52); /*0x100e8bb63*/
    v36 = sub_100D903F0(v10, v11, 10); /*0x100e8bb70*/
    if ( v36 )
    {
      v16 = v42; /*0x100e8bbe2*/
      v35 = construct_port_channel_vmc_data_msg(v36, v42, (unsigned int)v41); /*0x100e8bbee*/
      if ( v35 )
      {
        v22 = *(_QWORD *)(v35 + 24); /*0x100e8bc5c*/
        v40 = (void *)spice_marshaller_linearize(v22, 0, &v39, &v38); /*0x100e8bc6d*/
        if ( v40 && v39 )
        {
          if ( *(_QWORD *)(v36 + 24) )
          {
            LOBYTE(__b[0]) = 10; /*0x100e8bd44*/
            __b[1] = v39; /*0x100e8bd4c*/
            HIBYTE(__b[0]) = *(_BYTE *)(*(_QWORD *)(v36 + 24) + 1392LL); /*0x100e8bd5e*/
            sub_100E8BF30(thread_proxy_fd_session, __b, 4); /*0x100e8bd71*/
            v29 = v40; /*0x100e8bd7a*/
            sub_100E8BF30(thread_proxy_fd_session, v40, (unsigned int)v39); /*0x100e8bd87*/
            if ( (unsigned int)spice_util_get_debug(thread_proxy_fd_session, v29, v30, v31, v32, v33)
              && spice_gtk_log_level < 1 )
            {
              g_log(
                (unsigned int)"GSpice",
                128,
                (unsigned int)"[%-38s:%4d] fd: %d, Successfully wrote %zu bytes of port data to proxy socket",
                (unsigned int)"spice_session_write_port_data",
                965,
                *(_DWORD *)(v43 + 24),
                v39);
            }
          }
          else
          {
            if ( (unsigned int)spice_util_get_debug(v22, 0, v23, v24, v25, v26) ) /*0x100e8bcf2*/
              g_log( /*0x100e8bd22*/
                (unsigned int)"GSpice",
                8,
                (unsigned int)"[%-38s:%4d] Port channel private data is NULL - cannot access proxy link ID",
                (unsigned int)"spice_session_write_port_data",
                956,
                v28);
            set_fd_session_flag(v43, 16, 957); /*0x100e8bd3a*/
          }
        }
        else
        {
          if ( (unsigned int)spice_util_get_debug(v22, 0, v23, v24, v25, v26) ) /*0x100e8bc8c*/
            g_log( /*0x100e8bcbc*/
              (unsigned int)"GSpice",
              8,
              (unsigned int)"[%-38s:%4d] Failed to marshall port channel data - invalid output",
              (unsigned int)"spice_session_write_port_data",
              951,
              v27);
          set_fd_session_flag(v43, 16, 952); /*0x100e8bcd4*/
        }
      }
      else
      {
        if ( (unsigned int)spice_util_get_debug(v36, v16, v17, v18, v19, v20) ) /*0x100e8bc02*/
          g_log( /*0x100e8bc32*/
            (unsigned int)"GSpice",
            8,
            (unsigned int)"[%-38s:%4d] Failed to construct port channel VMC data message",
            (unsigned int)"spice_session_write_port_data",
            945,
            v21);
        set_fd_session_flag(v43, 16, 946); /*0x100e8bc4a*/
      }
    }
    else
    {
      if ( (unsigned int)spice_util_get_debug(v10, v11, v12, v13, v14, v15) ) /*0x100e8bb84*/
        g_log( /*0x100e8bbbc*/
          (unsigned int)"GSpice",
          8,
          (unsigned int)"[%-38s:%4d] Failed to lookup port channel with ID %d",
          (unsigned int)"spice_session_write_port_data",
          939,
          *(_DWORD *)(v43 + 52));
      set_fd_session_flag(v43, 16, 940); /*0x100e8bbd4*/
    }
    if ( v38 && v40 ) /*0x100e8bdfa*/
    {
      free(v40); /*0x100e8be04*/
      v40 = 0; /*0x100e8be09*/
    }
    if ( v35 ) /*0x100e8be16*/
      sub_100DA94B0(v35); /*0x100e8be20*/
    return spice_session_channels_mutex_unlock(*(_QWORD *)(v43 + 264)); /*0x100e8be38*/
  }
  else
  {
    if ( (unsigned int)spice_util_get_debug(v4, 6, v5, v6, v7, v8) ) /*0x100e8baf2*/
      g_log( /*0x100e8bb22*/
        (unsigned int)"GSpice",
        8,
        (unsigned int)"[%-38s:%4d] Failed to retrieve SPICE proxy socket - connection unavailable",
        (unsigned int)"spice_session_write_port_data",
        932,
        v9);
    return set_fd_session_flag(v43, 16, 933); /*0x100e8bb3a*/
  }
}
