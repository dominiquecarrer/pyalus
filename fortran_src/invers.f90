Recursive Function invers (M)
  ! calculate the inverse of a symmetric matrix M
      Real, Dimension (:, :), Intent (In) :: M
      Real, Dimension (Size(M, 1), Size(M, 1)) :: invers

      Real, Dimension (Size(M, 1), Size(M, 1)) :: A
      Real, Dimension (Size(M, 1)) :: b
      Integer, Dimension (Size(M, 1)) :: indx
      Integer :: I, J, N
      Real :: d

      Interface
         Subroutine ludcmp (A, indx, d)
            Use nrtype
            Real (SP), Dimension (:, :), Intent (Inout) :: A
            Integer (I4B), Dimension (:), Intent (Out) :: indx
            Real (SP), Intent (Out) :: d
         End Subroutine ludcmp
         Subroutine lubksb (A, indx, b)
            Use nrtype
            Real (SP), Dimension (:, :), Intent (In) :: A
            Integer (I4B), Dimension (:), Intent (In) :: indx
            Real (SP), Dimension (:), Intent (Inout) :: b
         End Subroutine lubksb
      End Interface

      A = M
      N = Size (M, 1)

  ! LU decomposition
      Call ludcmp (A, indx, d)

  ! calculate the inverse
      Do I = 1, N
         b = 0.
         b (I) = 1.
         Call lubksb (A, indx, b)
         invers (:, I) = b
      End Do

  ! restore symmetry of the matrix
      Do I = 1, N
         Do J = I + 1, N
            invers (I, J) = 0.5 * (invers(I, J)+invers(J, I))
            invers (J, I) = invers (I, J)
         End Do
      End Do

End Function invers
