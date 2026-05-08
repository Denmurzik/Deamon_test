#include "testlib.h"
using namespace std;

static const int B = 3;
static const int N = B*B;
vector<vector<string>> inputs;

bool isnum(char ch) { return ch >= '1' && ch <= '9'; }

int checkSolution(InStream &str) {
    for (int tt = 0; tt < inputs.size(); tt++) {
        vector<string> sol;
        for (int i = 0; i < N; i++) {
            string row = str.readToken();
            str.ensuref(row.size() == N, "T%d,R%d: row length is %d instead of %d", tt, i, int(row.size()), N);
            for (int j = 0; j < N; j++) {
                char ch = row[j];
                str.ensuref(isnum(ch), "T%d,R%d,C%d: character %d (%c) forbidden", tt, i, j, int(ch), ch);
            }
            sol.push_back(row);
        }

        auto CheckBlock = [&](int sr, int sc, int er, int ec) -> void {
            map<int, pair<int, int>> used;
            for (int i = sr; i < er; i++)
                for (int j = sc; j < ec; j++) {
                    pair<int, int> cell(i, j);
                    char ch = sol[i][j];
                    if (used.count(ch))
                        str.ensuref(false, "T%d: digit %c met both in (%d,%d) and (%d,%d)", tt, ch, i, j, used[ch].first, used[ch].second);
                    used[ch] = cell;
                }
        };

        for (int i = 0; i < N; i++)
            CheckBlock(i, 0, i+1, N);
        for (int i = 0; i < N; i++)
            CheckBlock(0, i, N, i+1);
        for (int i = 0; i < B; i++)
            for (int j = 0; j < B; j++)
                CheckBlock(i*B, j*B, i*B+B, j*B+B);

        auto input = inputs[tt];
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                str.ensuref(!isnum(input[i][j]) || input[i][j] == sol[i][j], "T%d,R%d,C%d: solution digit %c incompatible with input %c", tt, i, j, sol[i][j], input[i][j]);
    }

    return true;
}

int main(int argc, char **argv) {
    setName("sudoku checker");
    registerTestlibCmd(argc, argv);

    int tests = inf.readInt();
    for (int tt = 0; tt < tests; tt++) {
        vector<string> input;
        for (int i = 0; i < N; i++)
            input.push_back(inf.readToken());
        inputs.push_back(input);
    }

    int juryAns = checkSolution(ans);
    int partAns = checkSolution(ouf);

    if (partAns < juryAns)
        quitf(_wa, "Participant solution is worse: %d < %d", partAns, juryAns);
    if (partAns > juryAns)
        quitf(_fail, "Participant solution is BETTER: %d > %d", partAns, juryAns);

    quitf(_ok, "%d tests", tests);
}
