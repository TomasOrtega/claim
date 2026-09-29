import Lean
import Lean.Replay
open Lean

partial def audit (env trusted : Environment) (name : Name) (seen : NameSet := {}) : IO NameSet := do
  if seen.contains name then return seen
  let some ci := env.find? name | throw <| IO.userError s!"missing constant: {name}"
  let mut seen := seen.insert name
  if let .axiomInfo _ := ci then
    unless [``propext, ``Classical.choice, ``Quot.sound].contains name &&
        (trusted.find? name).any (fun original =>
          original.type == ci.type && original.levelParams == ci.levelParams) do
      throw <| IO.userError s!"unsupported axiom: {name}"
  let mut deps := ci.type.getUsedConstants ++ (ci.value? true).toArray.flatMap Expr.getUsedConstants
  if let .inductInfo value := ci then
    deps := deps ++ value.ctors.toArray
  for dep in deps do
    seen ← audit env trusted dep seen
  return seen

unsafe def main (args : List String) : IO Unit := do
  let mod :: decl :: paths := args | throw <| IO.userError "expected module, theorem and search paths"
  initSearchPath (← findSysroot)
  let trusted ← importModules #[{module := `Lean}] {}
  searchPathRef.modify (· ++ paths.map System.FilePath.mk)
  withImportModules #[{module := mod.toName}] {} fun env => do
    let some (.thmInfo thm) := env.find? decl.toName
      | throw <| IO.userError "expected a theorem declaration"
    discard <| (← mkEmptyEnvironment).toKernelEnv.replay env.constants.map₁
    discard <| audit env trusted decl.toName
    let statement ← (Meta.ppExpr thm.type).run'.toIO' {fileName := "", fileMap := default} {env}
    IO.println statement
