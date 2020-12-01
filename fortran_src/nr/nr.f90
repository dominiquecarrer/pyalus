MODULE nr

  INTERFACE pythag
     FUNCTION pythag_dp(a,b)
       USE nrtype
       REAL(DP), INTENT(IN) :: a,b
       REAL(DP) :: pythag_dp
     END FUNCTION pythag_dp
     FUNCTION pythag_sp(a,b)
       USE nrtype
       REAL(SP), INTENT(IN) :: a,b
       REAL(SP) :: pythag_sp
     END FUNCTION pythag_sp
  END INTERFACE

END MODULE nr

