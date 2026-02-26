; ModuleID = 'zlang_program'
source_filename = "zlang_program"

define i64 @add() {
entry:
  %x = alloca i64, align 8
  store i64 10, ptr %x, align 4
  %y = alloca i64, align 8
  store i64 20, ptr %y, align 4
  %x1 = load i64, ptr %x, align 4
  %y2 = load i64, ptr %y, align 4
  ret i64 0
}
