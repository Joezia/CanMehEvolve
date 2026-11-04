
Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    auto it = std::lower_bound(fields.begin(), fields.end(), fieldNum,
        [](const Field& field, FIT_UINT8 num) { return field.GetNum() < num; });
    
    if (it != fields.end() && it->GetNum() == fieldNum)
        return &*it;
    
    return FIT_NULL;
}
