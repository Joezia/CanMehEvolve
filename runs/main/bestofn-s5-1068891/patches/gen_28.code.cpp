
void Mesg::AddField(const Field& field)
{
    Field *existingField = GetField(field.GetNum());
    if (existingField == FIT_NULL) {
        fields.push_back(field);
    }
}
