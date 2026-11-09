FIT_BOOL Field::GetIsAccumulated() const
{
    const auto* p = profile;
    return p->fields[profileIndex].isAccumulated;
}
