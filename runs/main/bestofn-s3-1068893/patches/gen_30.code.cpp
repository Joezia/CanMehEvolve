
void Mesg::AddField(const Field& field)
{
    const std::size_t num = field.GetNum();
    for (auto& f : fields) {
        if (f.GetNum() == num) {
            f = field;
            return;
        }
    }
    fields.push_back(field);
}
