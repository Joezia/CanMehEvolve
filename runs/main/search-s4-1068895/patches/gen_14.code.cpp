
const Profile::FIELD_COMPONENT* Field::GetComponent(const FIT_UINT16 component) const
{
    return (component < GetNumComponents()) ? &profile->fields[profileIndex].components[component] : nullptr;
}
