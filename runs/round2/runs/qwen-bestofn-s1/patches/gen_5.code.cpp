
FIT_FLOAT64 Field::GetScale() const
{
    return (profile && profileIndex < profile->numFields) ? profile->fields[profileIndex].scale : 1.0;
}
