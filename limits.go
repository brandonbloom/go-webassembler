package webassembler

import (
	"math"
)

type Limits struct {
	Min U32
	Max U32
}

func MakeUnlimited(min U32) Limits {
	return Limits{min, math.MaxUint32}
}

func MakeLimits(min, max U32) Limits {
	return Limits{min, max}
}

func (lim *Limits) IsUnlimited() bool {
	return lim.Max == math.MaxUint32
}
